"""Postcodeloterij custom component for Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_POSTCODE, PLATFORMS
from .coordinator import PostcodeloterijCoordinator

type PostcodeloterijConfigEntry = ConfigEntry[PostcodeloterijCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: PostcodeloterijConfigEntry
) -> bool:
    """Set up Postcodeloterij from a config entry."""
    coordinator = PostcodeloterijCoordinator(
        hass,
        postcode=entry.data[CONF_POSTCODE],
    )
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: PostcodeloterijConfigEntry
) -> bool:
    """Unload a Postcodeloterij config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
