"""Sensor platform for the Postcodeloterij integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PostcodeloterijConfigEntry
from .const import CONF_POSTCODE, DOMAIN
from .coordinator import PostcodeloterijCoordinator, PostcodeloterijData

_LOGGER = logging.getLogger(__name__)

# The DataUpdateCoordinator handles fan-out; HA's per-entity throttling adds nothing.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PostcodeloterijConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Postcodeloterij sensor entities from a config entry."""
    coordinator = entry.runtime_data
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([PostcodeloterijSensor(coordinator, entry)])


class PostcodeloterijSensor(
    CoordinatorEntity[PostcodeloterijCoordinator], SensorEntity
):
    """Sensor reporting the number of prizes won for a given postcode."""

    _attr_icon = "mdi:trophy"
    _attr_native_unit_of_measurement = "prizes"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_attribution = "Data provided by Postcodeloterij"

    def __init__(
        self,
        coordinator: PostcodeloterijCoordinator,
        entry: PostcodeloterijConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        postcode: str = entry.data[CONF_POSTCODE]

        self._attr_unique_id = postcode
        self._attr_name = f"Postcodeloterij {postcode}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, postcode)},
            name=f"Postcodeloterij {postcode}",
            manufacturer="Postcodeloterij",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.postcodeloterij.nl",
        )

    @property
    def _data(self) -> PostcodeloterijData | None:
        return self.coordinator.data

    @property
    def native_value(self) -> int | None:
        if self._data is None:
            return None
        return self._data.prize_count

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self._data is None:
            return {}
        return {
            "prizes": self._data.prizes,
            "period": self._data.period,
            "prize_img_url": self._data.prize_img_url,
            "prize_description": self._data.prize_description,
            "prize_more_info_url": self._data.prize_more_info_url,
        }
