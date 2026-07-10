# Working in this repository

This is a Home Assistant custom integration that reports Nationale
Postcode Loterij prize counts for a given postcode. Distributed via HACS;
not part of HA core.

## Always consult HA developer documentation

Home Assistant's integration patterns evolve continuously. **Do not rely
on memory of past patterns** — fetch the canonical page before changing
a topic area, and check the developer blog before introducing anything
you only "know" from training data.

| When you change | Fetch first |
|---|---|
| Entity properties, naming, lifecycle, attributes | https://developers.home-assistant.io/docs/core/entity/ |
| Sensor specifics (state/device classes, units) | https://developers.home-assistant.io/docs/core/entity/sensor |
| Config flow, options flow, reauth, reconfigure | https://developers.home-assistant.io/docs/config_entries_config_flow_handler |
| DataUpdateCoordinator pattern | https://developers.home-assistant.io/docs/integration_fetching_data |
| Quality scale rules | https://developers.home-assistant.io/docs/core/integration-quality-scale |
| Diagnostics | https://developers.home-assistant.io/docs/core/integration/diagnostics |
| Translations | https://developers.home-assistant.io/docs/internationalization/core |

Branding is handled by the local `brand/` folder (HACS reads `icon.png`
from it). The official `home-assistant/brands` repo is for HA Core
integrations and does not apply here, so do not link to that flow when
proposing branding changes.

### Recent developer-facing changes

Before introducing patterns you only know from training data, check:

- https://developers.home-assistant.io/blog — API deprecations, new
  patterns, breaking changes. Recent posts trump older recollection.
- https://github.com/home-assistant/architecture/discussions — design
  decisions in flight that have not made it into stable docs yet.

## What is already in place

The integration is aligned with the **silver** quality scale tier. Don't
re-propose these as improvements:

- `quality_scale: "silver"` in manifest, minimum HA version `2024.7.0`
- `ConfigEntry.runtime_data` (the coordinator is the runtime data —
  no dataclass needed since there is only one thing to carry)
- `PARALLEL_UPDATES = 0` in `sensor.py`
- Coordinator is constructed with `config_entry=entry` so
  `self.config_entry` is available on the base class — do not
  refactor this to take just the postcode again
- **First refresh runs in `__init__.py`, before `async_forward_entry_setups`**
  — `async_setup_entry` awaits `coordinator.async_config_entry_first_refresh()`
  before forwarding (not in the `sensor.py` platform). Raising
  `ConfigEntryNotReady` from a *forwarded* platform is too late for HA to
  catch — it logs a warning and half-sets-up the entry. Do not move it back
  into a platform.
- Diagnostics handler in `diagnostics.py` (no credentials to redact —
  postcode-only setup)
- Tests for config flow, sensor, coordinator helpers (data update
  flow + the HTML `_parse_content` helper), diagnostics and
  setup/unload (`test_init.py` — successful setup+unload plus the
  first-refresh-failure → `SETUP_RETRY` path) — above 95% required for
  silver, current 97%.
- `_attr_attribution = "Data provided by Postcodeloterij"` on the sensors
- **`has_entity_name = True`** on every sensor, with `translation_key`
  routing names through `strings.json` + the language files, and icons in
  `icons.json` (no `_attr_icon`, no `_attr_name`) — the suite-wide
  pattern. The postcode lives on the *device* name
  (`"Postcodeloterij <postcode>"`), which prefixes the entity names.
  Existing installs keep their entity ids via the registry; new installs
  get `sensor.postcodeloterij_<postcode>_prizes`. Shipped in **1.3.0**
  as a minor (user decision): the release notes call out the renamed
  friendly names and that entity ids are preserved, which is the part
  automations depend on. No follow-up needed.
- `_attr_translation_key = "prizes"` on the prizes sensor; the unit is
  supplied via `entity.sensor.prizes.unit_of_measurement` in
  `strings.json` and the per-language translations (Dutch: `"prijzen"`).
  Do not re-introduce `_attr_native_unit_of_measurement` — translated
  units are the HA-spec-compliant way to surface count-units.
- **Diagnostic `last_update` sensor** (`PostcodeloterijLastUpdateSensor`,
  unique_id `{postcode}_last_update`, `EntityCategory.DIAGNOSTIC`, device
  class TIMESTAMP). Reads `coordinator.last_success_time`, stamped at the
  end of every successful `_async_update_data` — with a 12-hour poll a
  silently stale integration would otherwise go unnoticed for days.
- Sensor returns `None` (unavailable) when coordinator data is missing,
  not `0`, so consumers can tell "no prizes won" apart from "no data"
- Network errors raise `UpdateFailed` without an extra `_LOGGER.warning`
  — the `DataUpdateCoordinator` base class already logs the transition
  to unavailable once and the recovery once. Do not re-introduce
  per-error warning logs; they spam during long outages.

## Deliberately skipped (no plan to change)

- **`_unrecorded_attributes`** is *not* used. The sensor only polls
  twice a day, the attributes change once a month, and they're
  user-meaningful (prize titles, image URL, description). Recorder
  pressure is negligible; keeping history is the higher value.

## Repo-specific quirks

- **Polling cadence is 12 hours**, not the carrier-typical 5–15 minutes,
  because prizes are announced monthly. Don't drop this without thought.
- **Prize-month rollover**: the integration queries the *previous*
  calendar month, since prize lists for month M are published around
  the 1st of month M+1. See `_async_update_data`. Edge case: the very
  first day of a month, the new month has no prizes yet.
- **Hardcoded Chrome User-Agent**: `API_HEADERS` in `const.py` carries
  a desktop Chrome UA string. This is a workaround for postcodeloterij's
  bot detection — the request 403s without it. Do not refactor this away.
- The "prize description" attribute is extracted from a raw HTML blob
  via `_parse_content` (regex strip of `<a>` tags). PostcodeLoterij
  occasionally changes that HTML; if the description goes stale, this
  is the place to look.

## Running tests

```
python -m pytest tests/ --cov=custom_components.postcodeloterij
```

Coverage must stay **above 95%** (the silver `test-coverage` rule on
developers.home-assistant.io). Current coverage is 96%. Run before
committing.
