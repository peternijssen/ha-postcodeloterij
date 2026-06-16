"""Tests for PostcodeloterijCoordinator data parsing."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.postcodeloterij.coordinator import (
    PostcodeloterijCoordinator,
    PostcodeloterijData,
)

POSTCODE = "1234AB"


def _mock_entry(postcode: str = POSTCODE) -> MagicMock:
    entry = MagicMock()
    entry.data = {"postcode": postcode}
    entry.options = {}
    return entry


API_RESPONSE_NO_PRIZES = {
    "prizeCount": 0,
    "wonPrizes": [],
    "enrichedData": [],
}

API_RESPONSE_WITH_PRIZE = {
    "prizeCount": 1,
    "wonPrizes": [{"description": "Straatprijs PL"}],
    "enrichedData": [
        {
            "prizeTitle": "Straatprijs",
            "prizeImgUrl": "https://example.com/img.png",
            "content": '<p>Gefeliciteerd! <a href="https://example.com/faq">Meer info</a></p>',
        }
    ],
}


def _mock_response(payload: dict):
    response = AsyncMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=payload)
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)
    return response


async def test_no_prizes(hass):
    coordinator = PostcodeloterijCoordinator(hass, _mock_entry())

    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(return_value=_mock_response(API_RESPONSE_NO_PRIZES))
        mock_session_fn.return_value = session

        data = await coordinator._async_update_data()

    assert isinstance(data, PostcodeloterijData)
    assert data.prize_count == 0
    assert data.prizes == []
    assert data.prize_img_url is None
    assert data.prize_description is None
    assert data.prize_more_info_url is None


async def test_with_prize(hass):
    coordinator = PostcodeloterijCoordinator(hass, _mock_entry())

    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(return_value=_mock_response(API_RESPONSE_WITH_PRIZE))
        mock_session_fn.return_value = session

        data = await coordinator._async_update_data()

    assert data.prize_count == 1
    assert data.prizes == ["Straatprijs"]
    assert data.prize_img_url == "https://example.com/img.png"
    assert data.prize_description == "Gefeliciteerd!"
    assert data.prize_more_info_url == "https://example.com/faq"


async def test_enriched_title_preferred_over_won_prizes(hass):
    """enrichedData prizeTitle takes priority over wonPrizes description."""
    coordinator = PostcodeloterijCoordinator(hass, _mock_entry())

    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(return_value=_mock_response(API_RESPONSE_WITH_PRIZE))
        mock_session_fn.return_value = session

        data = await coordinator._async_update_data()

    assert "Straatprijs" in data.prizes
    assert "Straatprijs PL" not in data.prizes


async def test_period_is_previous_month(hass, freezer):
    """The queried period is always the calendar month before today."""
    freezer.move_to("2026-05-15")
    coordinator = PostcodeloterijCoordinator(hass, _mock_entry())

    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(return_value=_mock_response(API_RESPONSE_NO_PRIZES))
        mock_session_fn.return_value = session

        data = await coordinator._async_update_data()

    assert data.period == "04-2026"


async def test_api_error_raises_update_failed(hass):
    import aiohttp
    from homeassistant.helpers.update_coordinator import UpdateFailed

    coordinator = PostcodeloterijCoordinator(hass, _mock_entry())

    with patch(
        "custom_components.postcodeloterij.coordinator.async_get_clientsession"
    ) as mock_session_fn:
        session = MagicMock()
        session.post = MagicMock(side_effect=aiohttp.ClientError("connection failed"))
        mock_session_fn.return_value = session

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
