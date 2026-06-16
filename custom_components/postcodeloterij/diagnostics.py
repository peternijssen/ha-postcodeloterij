"""Diagnostics support for the Postcodeloterij integration."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from . import PostcodeloterijConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: PostcodeloterijConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a Postcodeloterij config entry."""
    coordinator = entry.runtime_data
    last_data = coordinator.data
    return {
        "entry_data": dict(entry.data),
        "last_update_success": coordinator.last_update_success,
        "data": asdict(last_data) if last_data is not None else None,
    }
