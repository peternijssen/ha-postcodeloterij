"""Coordinator for the Postcodeloterij integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_HEADERS, API_URL, DOMAIN, POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass
class PostcodeloterijData:
    prize_count: int = 0
    prizes: list[str] = field(default_factory=list)
    period: str = ""
    prize_img_url: str | None = None


class PostcodeloterijCoordinator(DataUpdateCoordinator[PostcodeloterijData]):
    """Coordinator that polls the Postcodeloterij API on a fixed schedule."""

    def __init__(self, hass: HomeAssistant, postcode: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{postcode}",
            update_interval=timedelta(seconds=POLL_INTERVAL),
        )
        self._postcode = postcode

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
            raise UpdateFailed(
                f"Could not fetch prize data for {self._postcode}: {err}"
            ) from err

        # enrichedData carries the clean prize title; wonPrizes.description
        # appends a lottery-type suffix (e.g. "Pizzaprijs PL") that is
        # not useful to end users.
        prizes = [
            e.get("prizeTitle", "")
            for e in data.get("enrichedData", [])
        ] or [
            p.get("description", "")
            for p in data.get("wonPrizes", [])
        ]

        _LOGGER.debug(
            "Postcodeloterij %s — period %s, prizes: %d",
            self._postcode,
            period_key,
            data.get("prizeCount", 0),
        )

        enriched = data.get("enrichedData") or []
        prize_img_url = enriched[0].get("prizeImgUrl") if enriched else None

        return PostcodeloterijData(
            prize_count=data.get("prizeCount", 0),
            prizes=prizes,
            period=target.strftime("%m-%Y"),
            prize_img_url=prize_img_url,
        )
