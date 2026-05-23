"""Unit tests for the _parse_content helper in coordinator.py."""
import pytest

from custom_components.postcodeloterij.coordinator import _parse_content


def test_none_returns_none():
    assert _parse_content(None) == (None, None)


def test_empty_string_returns_none():
    assert _parse_content("") == (None, None)


def test_plain_text_no_link():
    description, url = _parse_content("<p>Een mooie prijs</p>")
    assert description == "Een mooie prijs"
    assert url is None


def test_anchor_text_is_stripped():
    content = '<p>Win een auto <a href="https://example.com">Meer info</a></p>'
    description, url = _parse_content(content)
    assert "Meer info" not in description
    assert "Win een auto" in description


def test_href_is_extracted():
    content = '<p>Prijs <a href="https://www.postcodeloterij.nl/faq/pizzaprijs">meer info</a></p>'
    _, url = _parse_content(content)
    assert url == "https://www.postcodeloterij.nl/faq/pizzaprijs"


def test_html_entities_are_unescaped():
    description, _ = _parse_content("<p>Waarde &euro; 25.000</p>")
    assert "€" in description


def test_multiple_tags_collapsed():
    content = "<p>Eerste zin.</p><p>Tweede zin.</p>"
    description, _ = _parse_content(content)
    assert "Eerste zin." in description
    assert "Tweede zin." in description
    assert "\n" not in description


def test_whitespace_is_normalised():
    description, _ = _parse_content("<p>  Veel   spaties  </p>")
    assert "  " not in description
    assert description == "Veel spaties"


def test_only_anchor_returns_none_description():
    content = '<a href="https://example.com">Klik hier</a>'
    description, url = _parse_content(content)
    assert description is None
    assert url == "https://example.com"
