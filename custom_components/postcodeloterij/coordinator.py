"""Coordinator for the Postcodeloterij integration."""
from __future__ import annotations

import html as html_lib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_HEADERS, API_URL, CONF_POSTCODE, DOMAIN, POLL_INTERVAL

if TYPE_CHECKING:
    from . import PostcodeloterijConfigEntry

_LOGGER = logging.getLogger(__name__)


def _parse_content(content: str | None) -> tuple[str | None, str | None]:
    """Extract plain-text description and more-info URL from the HTML content field."""
    if not content:
        return None, None

    url_match = re.search(r'href="([^"]+)"', content)
    more_info_url = url_match.group(1) if url_match else None

    plain = re.sub(r"<a\b[^>]*>.*?</a>", "", content, flags=re.DOTALL)
    plain = re.sub(r"<[^>]+>", " ", plain)
    plain = html_lib.unescape(plain)
    plain = re.sub(r"\s+", " ", plain).strip()

    return plain or None, more_info_url


@dataclass
class PostcodeloterijData:
    prize_count: int = 0
    prizes: list[str] = field(default_factory=list)
    period: str = ""
    prize_img_url: str | None = None
    prize_description: str | None = None
    prize_more_info_url: str | None = None


class PostcodeloterijCoordinator(DataUpdateCoordinator[PostcodeloterijData]):
    """Coordinator that polls the Postcodeloterij API on a fixed schedule."""

    def __init__(
        self, hass: HomeAssistant, entry: PostcodeloterijConfigEntry
    ) -> None:
        postcode: str = entry.data[CONF_POSTCODE]
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{postcode}",
            update_interval=timedelta(seconds=POLL_INTERVAL),
        )
        self._postcode = postcode
        # Timestamp of the last successful poll, surfaced by a diagnostic
        # sensor. With a 12-hour poll interval a silently-stale integration
        # would otherwise go unnoticed for a long time.
        self.last_success_time: datetime | None = None

    async def _async_update_data(self) -> PostcodeloterijData:
        session = async_get_clientsession(self.hass)

        # Prizes for month M are published around the 1st of month M+1,
        # so we always query the previous calendar month.
        first_of_this_month = datetime.now().replace(day=1)
        target = (first_of_this_month - timedelta(days=1)).replace(day=1)
        period_key = f"{target.year}{target.month:02d}"
        url = API_URL.format(period_key)

        try:
            async with session.post(
                url,
                data={"query": self._postcode},
                headers=API_HEADERS,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            # DataUpdateCoordinator already logs UpdateFailed once on the
            # transition to unavailable and once on recovery — no need to
            # warn here as well.
            raise UpdateFailed(
                f"Could not fetch prize data for {self._postcode}: {err}"
            ) from err

        enriched = data.get("enrichedData") or []
        first = enriched[0] if enriched else {}

        # enrichedData carries the clean prize title; wonPrizes.description
        # appends a lottery-type suffix (e.g. "Pizzaprijs PL") that is
        # not useful to end users.
        prizes = [
            e.get("prizeTitle", "") for e in enriched
        ] or [
            p.get("description", "") for p in data.get("wonPrizes", [])
        ]

        prize_description, prize_more_info_url = _parse_content(first.get("content"))

        _LOGGER.debug(
            "Postcodeloterij %s — period %s, prizes: %d",
            self._postcode,
            period_key,
            data.get("prizeCount", 0),
        )

        self.last_success_time = datetime.now(timezone.utc)
        return PostcodeloterijData(
            prize_count=data.get("prizeCount", 0),
            prizes=prizes,
            period=target.strftime("%m-%Y"),
            prize_img_url=first.get("prizeImgUrl"),
            prize_description=prize_description,
            prize_more_info_url=prize_more_info_url,
        )
