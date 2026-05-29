# Postcodeloterij — Home Assistant Integration

A custom component for [Home Assistant](https://www.home-assistant.io/) that checks whether your postal code has won a prize in the Dutch [Postcodeloterij](https://www.postcodeloterij.nl/) monthly draw.

## Features

- Configure one or more postal codes through the Home Assistant UI
- One sensor per postal code showing the number of prizes won
- Prize descriptions, image, and draw period exposed as attributes
- Checks every 12 hours

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

## Sensors

Each configured postal code gets one sensor:

| Entity | Description |
|--------|-------------|
| `sensor.postcodeloterij_<postcode>` | Number of prizes won in the most recent draw |

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

This is an independent, community-built project with no affiliation, endorsement, or connection to Postcodeloterij or any of its subsidiaries. The Postcodeloterij API is undocumented and may change without notice.
