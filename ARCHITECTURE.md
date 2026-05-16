# Architecture

This document describes the internal structure of the Postcodeloterij integration, how the components relate to each other, and the key design decisions made. It is intended as a reference for AI agents and contributors working on the codebase.

## Project layout

```
custom_components/postcodeloterij/
├── __init__.py        # Entry point: setup, teardown, wires up coordinator
├── config_flow.py     # UI config flow: postcode entry + format validation
├── const.py           # All constants: API URL, domain, poll interval
├── coordinator.py     # DataUpdateCoordinator: polls API, month-fallback logic
├── sensor.py          # One sensor entity per config entry (postcode)
├── manifest.json      # HA integration manifest
├── strings.json       # UI strings (source of truth, duplicated into translations/)
└── translations/
    ├── en.json        # English translations
    └── nl.json        # Dutch translations
```

## Data flow

```
Postcodeloterij public REST API
           │
           ▼
PostcodeloterijCoordinator (coordinator.py)
  polls every 12 hours
  tries current month → falls back to previous month
           │
           ▼
PostcodeloterijSensor (sensor.py)
  one entity per config entry (postcode)
           │
           ▼
  Home Assistant entity registry
```

## Component responsibilities

### `__init__.py`
- Called by HA when the integration is loaded (`async_setup_entry`)
- Creates one `PostcodeloterijCoordinator` per config entry
- Stores the coordinator in `hass.data[DOMAIN][entry.entry_id]`
- Forwards setup to the `sensor` platform
- On unload (`async_unload_entry`), tears down platforms and cleans up `hass.data`

### `config_flow.py`
- Validates the postcode format against `^\d{4}[A-Z]{2}$` before saving
- Normalises the user input to uppercase
- Makes a live POST request to the current month's API endpoint to verify connectivity
- Sets the unique ID to the postcode to prevent duplicate entries

### `const.py`
- Single source of truth for all magic values
- `API_URL` — the Postcodeloterij public REST endpoint; requires a `{YYYYMM}` period to be formatted in
- `POLL_INTERVAL` — 43200 seconds (12 hours); draws happen once a month so this is more than sufficient

### `coordinator.py`
- `PostcodeloterijCoordinator` — polls the API and returns a `PostcodeloterijData` dataclass
- Uses the HA-managed `aiohttp.ClientSession` (`async_get_clientsession`)
- Raises `UpdateFailed` only after exhausting both month candidates

### `sensor.py`
- `PostcodeloterijSensor` — one entity per config entry
- `native_value` is the integer `prize_count`
- `extra_state_attributes` exposes `prizes` (list of prize titles) and `period` (draw month as `MM-YYYY`)

## Key design decisions

### One config entry per postcode
Each postcode is its own config entry rather than storing a list in a single entry. This follows standard HA patterns: it makes entities easy to enable/disable individually, avoids custom UI complexity, and keeps the coordinator logic stateless per postcode.

### Always querying the previous month
Prizes for month M are published around the 1st of month M+1. The coordinator therefore always queries the previous calendar month — no fallback logic is needed. Querying the current month would be unreliable because the API returns `prizeCount: 0` whether the draw is pending or simply yielded no prize, making the two cases indistinguishable.

### `enrichedData.prizeTitle` over `wonPrizes.description`
The API returns two parallel arrays. `wonPrizes[].description` appends a lottery-type suffix to the prize name (e.g. `"Pizzaprijs PL"`). `enrichedData[].prizeTitle` contains the clean, user-facing name (e.g. `"Pizzaprijs"`). The coordinator uses `prizeTitle` with a fallback to `description` in case `enrichedData` is absent.

## `hass.data` structure

```python
hass.data["postcodeloterij"] = {
    "<entry_id>": PostcodeloterijCoordinator,
}
```

## Sensor unique ID pattern

| Sensor class | Unique ID | Example |
|---|---|---|
| `PostcodeloterijSensor` | `{postcode}` | `1234AB` |

The postcode is stored in uppercase in the config entry and used as-is for the unique ID.
