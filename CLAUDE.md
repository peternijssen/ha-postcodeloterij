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
- Diagnostics handler in `diagnostics.py` (no credentials to redact —
  postcode-only setup)
- Tests for config flow, sensor, coordinator helpers (data update
  flow + the HTML `_parse_content` helper) and diagnostics — above
  95% required for silver, current 96%. There is no `test_init.py`;
  the setup/unload path is exercised indirectly via the config-flow
  and coordinator tests.
- `_attr_attribution = "Data provided by Postcodeloterij"` on the sensor
- `_attr_translation_key = "prizes"` on the sensor; the unit is supplied
  via `entity.sensor.prizes.unit_of_measurement` in `strings.json` and
  the per-language translations (Dutch: `"prijzen"`). Do not re-introduce
  `_attr_native_unit_of_measurement` — translated units are the
  HA-spec-compliant way to surface count-units.
- Sensor returns `None` (unavailable) when coordinator data is missing,
  not `0`, so consumers can tell "no prizes won" apart from "no data"
- Network errors raise `UpdateFailed` without an extra `_LOGGER.warning`
  — the `DataUpdateCoordinator` base class already logs the transition
  to unavailable once and the recovery once. Do not re-introduce
  per-error warning logs; they spam during long outages.

## Planned for the next major version

- **`has_entity_name`** is *not yet* used on this integration. Adopting
  it is a Bronze-tier requirement per HA docs ("There are no exceptions
  to this rule"), but switching it on now would change friendly names
  for existing dashboards and automations. It will land in the next
  breaking-change release alongside any other naming/structure shifts.
  Until then, the silver claim in the manifest is pragmatic rather than
  strict-by-the-book.

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
