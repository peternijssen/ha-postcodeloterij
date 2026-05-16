"""Config flow for the Postcodeloterij integration."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_HEADERS, API_URL, CONF_POSTCODE, DOMAIN

_POSTCODE_RE = re.compile(r"^\d{4}[A-Z]{2}$")

_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_POSTCODE): str,
    }
)


class PostcodeloterijConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the UI-driven configuration flow for the Postcodeloterij integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the postcode form and validate on submit."""
        errors: dict[str, str] = {}

        if user_input is not None:
            postcode = user_input[CONF_POSTCODE].strip().upper()

            if not _POSTCODE_RE.match(postcode):
                errors[CONF_POSTCODE] = "invalid_postcode"
            else:
                try:
                    await self._async_test_connection(postcode)
                except aiohttp.ClientError:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(postcode)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=postcode,
                        data={CONF_POSTCODE: postcode},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=_USER_SCHEMA,
            errors=errors,
        )

    async def _async_test_connection(self, postcode: str) -> None:
        """Verify the API is reachable with a quick request."""
        now = datetime.now()
        url = API_URL.format(f"{now.year}{now.month:02d}")
        session = async_get_clientsession(self.hass)
        async with session.post(
            url,
            data={"query": postcode},
            headers=API_HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            resp.raise_for_status()
