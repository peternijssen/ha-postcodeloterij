"""Tests for the Postcodeloterij sensor."""
from unittest.mock import MagicMock

from custom_components.postcodeloterij.coordinator import PostcodeloterijData
from custom_components.postcodeloterij.sensor import PostcodeloterijSensor


def _make_entry(postcode: str = "1234AB") -> MagicMock:
    entry = MagicMock()
    entry.data = {"postcode": postcode}
    return entry


def _make_coordinator(data: PostcodeloterijData | None) -> MagicMock:
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.last_update_success = data is not None
    return coordinator


def test_native_value_returns_prize_count():
    data = PostcodeloterijData(
        prize_count=3,
        prizes=["Pizzaprijs", "Straatprijs", "PostcodeKanjer"],
        period="05-2026",
    )
    sensor = PostcodeloterijSensor(_make_coordinator(data), _make_entry())
    assert sensor.native_value == 3


def test_native_value_is_none_when_data_missing():
    """When no data is available the sensor should be unavailable, not zero."""
    sensor = PostcodeloterijSensor(_make_coordinator(None), _make_entry())
    assert sensor.native_value is None


def test_attributes_expose_prize_details():
    data = PostcodeloterijData(
        prize_count=2,
        prizes=["Straatprijs", "Pizzaprijs"],
        period="05-2026",
        prize_img_url="https://example.com/img.png",
        prize_description="You won a free pizza",
        prize_more_info_url="https://example.com/more-info",
    )
    sensor = PostcodeloterijSensor(_make_coordinator(data), _make_entry())
    attrs = sensor.extra_state_attributes
    assert attrs["prizes"] == ["Straatprijs", "Pizzaprijs"]
    assert attrs["period"] == "05-2026"
    assert attrs["prize_img_url"] == "https://example.com/img.png"
    assert attrs["prize_description"] == "You won a free pizza"
    assert attrs["prize_more_info_url"] == "https://example.com/more-info"


def test_attributes_empty_when_data_missing():
    sensor = PostcodeloterijSensor(_make_coordinator(None), _make_entry())
    assert sensor.extra_state_attributes == {}


def test_sensor_uses_postcode_as_unique_id_and_friendly_name():
    sensor = PostcodeloterijSensor(_make_coordinator(None), _make_entry("5678CD"))
    assert sensor.unique_id == "5678CD"
    assert sensor.name == "Postcodeloterij 5678CD"
