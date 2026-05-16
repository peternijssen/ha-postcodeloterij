# Postcodeloterij — Home Assistant Integration

A custom component for [Home Assistant](https://www.home-assistant.io/) that checks whether your postal code has won a prize in the Dutch [Postcodeloterij](https://www.postcodeloterij.nl/) monthly draw.

## Features

- Configure one or more postal codes through the Home Assistant UI
- One sensor per postal code showing the number of prizes won
- Prize descriptions and the draw period are exposed as attributes
- Checks every 12 hours (draws only happen once a month, so this is more than sufficient)

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** and click **+ Explore & Download Repositories**
3. Search for **Postcodeloterij** and install it
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/postcodeloterij` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → + Add Integration**
2. Search for **Postcodeloterij**
3. Enter your postal code (format: `1234AB`)
4. Repeat for each additional postal code you want to track

## Sensor

Each configured postal code gets one sensor:

| Property | Value |
|---|---|
| Entity ID | `sensor.postcodeloterij_1234ab` |
| State | Number of prizes won (integer) |
| Unit | prizes |
| Icon | `mdi:trophy` |

### Attributes

| Attribute | Description |
|---|---|
| `prizes` | List of prize descriptions (empty when no prizes won) |
| `period` | The draw period checked, formatted as `MM-YYYY` |
| `prize_img_url` | URL of the prize image, or `null` when no prize was won |

### Example state

```yaml
state: 1
attributes:
  prizes:
    - "Straatprijs €25.000"
  period: "05-2026"
```

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
      service: notify.all_devices
      data:
        title: "Postcodeloterij uitslag"
        message: >
          Deze maand heb je {{ states('sensor.postcodeloterij_1234ab') }}x prijs!
          Namelijk {{ state_attr('sensor.postcodeloterij_1234ab', 'prizes') | join(', ') }}.
          Gefeliciteerd!
        data:
          ttl: 0
          priority: high
```

The condition on `now().day == 2` gives the Postcodeloterij a day after the draw to publish results before the automation fires. Adjust the day and time to your preference.

## API

See [docs/api/](docs/api/) for the full API reference, including the request format, response structure, and field descriptions.

## Notes

- Prize data is fetched from the Postcodeloterij public API
- Prizes for month M are published around the 1st of month M+1, so the integration always checks the previous month's draw results

## Disclaimer

This integration and its documentation were generated with the assistance of AI tools. It is an independent, community-built project with no affiliation, endorsement, or connection to Postcodeloterij or any of its subsidiaries.

Use at your own risk. The Postcodeloterij API is undocumented and may change without notice, which could break this integration at any time.
