"""Tests for the Postcodeloterij setup/unload entry points."""
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState

from custom_components.postcodeloterij.const import CONF_POSTCODE, DOMAIN

_API_RESPONSE = {"prizeCount": 0, "wonPrizes": [], "enrichedData": []}


def _add_entry(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="1234ab",
        data={CONF_POSTCODE: "1234AB"},
    )
    entry.add_to_hass(hass)
    return entry


def _mock_response(payload: dict):
    response = AsyncMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=payload)
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)
    return response


@pytest.mark.asyncio
async def test_setup_and_unload(hass):
    """A successful setup loads the entry; unload tears it down cleanly."""
    entry = _add_entry(hass)
    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(return_value=_mock_response(_API_RESPONSE))
        mock_session_fn.return_value = session

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_setup_retries_when_first_refresh_fails(hass):
    """When the first data fetch fails, setup retries from the entry itself.

    The first refresh runs in __init__.py before platforms are forwarded, so a
    failure raises ConfigEntryNotReady from the entry setup (SETUP_RETRY) rather
    than — too late — from a forwarded platform.
    """
    entry = _add_entry(hass)
    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(side_effect=aiohttp.ClientError("connection failed"))
        mock_session_fn.return_value = session

        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.SETUP_RETRY
