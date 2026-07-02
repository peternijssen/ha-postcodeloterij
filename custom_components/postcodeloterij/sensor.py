"""Sensor platform for the Postcodeloterij integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
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
    async_add_entities([
        PostcodeloterijSensor(coordinator, entry),
        PostcodeloterijLastUpdateSensor(coordinator, entry),
    ])


def _build_device_info(postcode: str) -> DeviceInfo:
    """Return the DeviceInfo shared by all sensors for this postcode."""
    return DeviceInfo(
        identifiers={(DOMAIN, postcode)},
        name=f"Postcodeloterij {postcode}",
        manufacturer="Postcodeloterij",
        entry_type=DeviceEntryType.SERVICE,
        configuration_url="https://www.postcodeloterij.nl",
    )


class PostcodeloterijSensor(
    CoordinatorEntity[PostcodeloterijCoordinator], SensorEntity
):
    """Sensor reporting the number of prizes won for a given postcode."""

    _attr_has_entity_name = True
    _attr_translation_key = "prizes"
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
        self._attr_device_info = _build_device_info(postcode)

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


class PostcodeloterijLastUpdateSensor(
    CoordinatorEntity[PostcodeloterijCoordinator], SensorEntity
):
    """Diagnostic sensor reporting when the lottery API was last polled successfully.

    Updates on every successful coordinator refresh, even when the prize
    data itself is unchanged — with a 12-hour poll interval a silently
    stale integration would otherwise go unnoticed for a long time.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "last_update"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_attribution = "Data provided by Postcodeloterij"

    def __init__(
        self,
        coordinator: PostcodeloterijCoordinator,
        entry: PostcodeloterijConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        postcode: str = entry.data[CONF_POSTCODE]
        self._attr_unique_id = f"{postcode}_last_update"
        self._attr_device_info = _build_device_info(postcode)

    @property
    def native_value(self) -> datetime | None:
        """Return the timestamp of the last successful poll."""
        return self.coordinator.last_success_time
