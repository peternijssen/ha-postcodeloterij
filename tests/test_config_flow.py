"""Tests for the Postcodeloterij config flow."""
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from homeassistant.config_entries import SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType

from custom_components.postcodeloterij.const import CONF_POSTCODE, DOMAIN


@pytest.mark.asyncio
async def test_user_flow_creates_entry(hass):
    """Happy path: a valid postcode + reachable API yields a CREATE_ENTRY result."""
    with patch(
        "custom_components.postcodeloterij.config_flow.PostcodeloterijConfigFlow._async_test_connection",
        new=AsyncMock(return_value=None),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_POSTCODE: "1234ab"}
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    # Stored in uppercase, no whitespace
    assert result["title"] == "1234AB"
    assert result["data"] == {CONF_POSTCODE: "1234AB"}


@pytest.mark.asyncio
async def test_user_flow_rejects_invalid_postcode(hass):
    """An invalid postcode shows the invalid_postcode error and does not call the API."""
    with patch(
        "custom_components.postcodeloterij.config_flow.PostcodeloterijConfigFlow._async_test_connection",
        new=AsyncMock(),
    ) as mock_test:
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_POSTCODE: "not a postcode"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_POSTCODE: "invalid_postcode"}
    mock_test.assert_not_called()


@pytest.mark.asyncio
async def test_user_flow_cannot_connect(hass):
    """A network error on the test request surfaces cannot_connect."""
    with patch(
        "custom_components.postcodeloterij.config_flow.PostcodeloterijConfigFlow._async_test_connection",
        new=AsyncMock(side_effect=aiohttp.ClientError("boom")),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_POSTCODE: "1234AB"}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_user_flow_aborts_on_duplicate_postcode(hass):
    """Configuring the same postcode twice aborts the second flow."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    MockConfigEntry(
        domain=DOMAIN,
        unique_id="1234AB",
        data={CONF_POSTCODE: "1234AB"},
    ).add_to_hass(hass)

    with patch(
        "custom_components.postcodeloterij.config_flow.PostcodeloterijConfigFlow._async_test_connection",
        new=AsyncMock(return_value=None),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_POSTCODE: "1234AB"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
