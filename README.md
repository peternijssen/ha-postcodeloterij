# Postcodeloterij — Home Assistant Integration

[![Release](https://img.shields.io/github/v/release/peternijssen/ha-postcodeloterij.svg)](https://github.com/peternijssen/ha-postcodeloterij/releases)
[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 💬 Questions or feedback? Join the discussion on the [Home Assistant community](https://community.home-assistant.io/t/postcodeloterij-integration-dutch-postcode-lottery/1014788).

A custom component for [Home Assistant](https://www.home-assistant.io/) that checks whether your postal code has won a prize in the Dutch [Postcodeloterij](https://www.postcodeloterij.nl/) monthly draw.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Removal](#removal)
- [Sensors](#sensors)
- [Automation example](#automation-example)
- [Acknowledgements](#acknowledgements)
- [Disclaimer](#disclaimer)
- [License](#license)

## Features

- Configure one or more postal codes through the Home Assistant UI
- One sensor per postal code showing the number of prizes won
- Prize descriptions, image, and draw period exposed as attributes
- Checks every 12 hours

## Installation

### HACS (recommended)

This integration is available in the default [HACS](https://hacs.xyz) store —
no custom repository needed.

1. Open HACS and search for **Postcodeloterij**
2. Select it and click **Download**
3. Restart Home Assistant

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=peternijssen&repository=ha-postcodeloterij&category=integration)

### Manual

1. Copy the `custom_components/postcodeloterij` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → + Add Integration**
2. Search for **Postcodeloterij**
3. Enter your postal code (format: `1234AB`)
4. Repeat for each additional postal code you want to track

### Setup parameters

| Field | Description |
|---|---|
| Postal code | Your Dutch postal code in the `1234AB` format — four digits followed by two uppercase letters. No account or credentials are needed; the integration uses the public lottery results endpoint. |

### Options

This integration has no configurable options. The polling interval is fixed at 12 hours because lottery results are published monthly — there is no benefit to checking more often.

## Removal

Standard Home Assistant removal applies: **Settings → Devices & Services → Postcodeloterij → ⋮ → Delete**. No external cleanup is needed; deleting the config entry stops the polling.

## Sensors

Each configured postal code gets a device with two sensors:

| Entity | Description |
|--------|-------------|
| `sensor.postcodeloterij_<postcode>_prizes` | Number of prizes won in the most recent draw |
| `sensor.postcodeloterij_<postcode>_last_successful_update` | Diagnostic: when the lottery API last answered successfully |

Installations that existed before the naming switch keep their original entity id (`sensor.postcodeloterij_<postcode>`) — Home Assistant preserves entity ids across renames.

For the full attribute reference and draw timing details see [docs/sensors.md](docs/sensors.md).

## Automation example

Check for prizes on the 2nd of every month at 14:00 and send a priority notification if you won. Replace `1234ab` with your own postcode (lowercase, as HA generates it).

```yaml
automation:
  - id: postcodeloterij
    alias: "Postcodeloterij: Prijs"
    initial_state: "on"
    trigger:
      platform: time
      at: "14:00:00"
    condition:
      - "{{ now().day == 2 }}"
      - "{{ states('sensor.postcodeloterij_1234ab') | int(0) > 0 }}"
    action:
      action: notify.all_devices
      data:
        title: "Postcodeloterij uitslag"
        message: "{{ state_attr('sensor.postcodeloterij_1234ab', 'prize_description') }}"
        data:
          clickAction: "{{ state_attr('sensor.postcodeloterij_1234ab', 'prize_more_info_url') }}"
          image: "{{ state_attr('sensor.postcodeloterij_1234ab', 'prize_img_url') }}"
          ttl: 0
          priority: high
```

## Acknowledgements

This integration is based on the original work by [kvanhoorn](https://github.com/kvanhoorn/hass).

## Disclaimer

This is an independent, community-built project with no affiliation, endorsement, or connection to Postcodeloterij or any of its subsidiaries. The Postcodeloterij API is undocumented and may change without notice. The maintainers have not asked Postcodeloterij for permission to use this API; installing this integration may breach Postcodeloterij's Terms of Service. You take any risk that follows — account suspension, service disruption, etc. No warranty (see [LICENSE](LICENSE)).

## License

MIT
