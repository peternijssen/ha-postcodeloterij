"""Tests for the Postcodeloterij diagnostics handler."""
from unittest.mock import MagicMock

import pytest

from custom_components.postcodeloterij.coordinator import PostcodeloterijData
from custom_components.postcodeloterij.diagnostics import (
    async_get_config_entry_diagnostics,
)


def _entry(data: PostcodeloterijData | None, *, last_update_success: bool = True) -> MagicMock:
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.last_update_success = last_update_success

    entry = MagicMock()
    entry.data = {"postcode": "1234AB"}
    entry.runtime_data = coordinator
    return entry


@pytest.mark.asyncio
async def test_diagnostics_returns_entry_data_and_data():
    entry = _entry(
        PostcodeloterijData(prize_count=2, prizes=["a", "b"], period="05-2026")
    )
    result = await async_get_config_entry_diagnostics(MagicMock(), entry)
    assert result["entry_data"] == {"postcode": "1234AB"}
    assert result["last_update_success"] is True
    assert result["data"]["prize_count"] == 2
    assert result["data"]["prizes"] == ["a", "b"]


@pytest.mark.asyncio
async def test_diagnostics_handles_missing_data():
    entry = _entry(None, last_update_success=False)
    result = await async_get_config_entry_diagnostics(MagicMock(), entry)
    assert result["data"] is None
    assert result["last_update_success"] is False
