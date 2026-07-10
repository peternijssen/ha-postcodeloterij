"""Postcodeloterij custom component for Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import PostcodeloterijCoordinator

type PostcodeloterijConfigEntry = ConfigEntry[PostcodeloterijCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: PostcodeloterijConfigEntry
) -> bool:
    """Set up Postcodeloterij from a config entry."""
    coordinator = PostcodeloterijCoordinator(hass, entry)
    entry.runtime_data = coordinator

    # Fetch initial data here, before forwarding to platforms. Raising
    # ConfigEntryNotReady from a forwarded platform is too late for HA to catch
    # cleanly (it logs a warning and half-sets-up the entry); doing the first
    # refresh here lets a transient failure fail the whole entry so HA retries
    # it with backoff.
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: PostcodeloterijConfigEntry
) -> bool:
    """Unload a Postcodeloterij config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
