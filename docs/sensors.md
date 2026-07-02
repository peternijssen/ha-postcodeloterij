# Sensors

Full reference for all sensors provided by the Postcodeloterij integration.

## `sensor.postcodeloterij_<postcode>_prizes`

One sensor per configured postal code. (Installations from before the naming switch keep their original `sensor.postcodeloterij_<postcode>` entity id.)

**State:** number of prizes won in the most recent draw (integer, unit: `prizes`)

### Attributes

| Attribute | Description |
|-----------|-------------|
| `prizes` | List of prize descriptions (empty when no prizes won) |
| `period` | The draw period checked, formatted as `MM-YYYY` |
| `prize_img_url` | URL of the prize image, or `null` when no prize was won |
| `prize_description` | Plain-text prize description, or `null` when no prize was won |
| `prize_more_info_url` | URL to the prize detail page on the Postcodeloterij FAQ, or `null` when no prize was won |

### Example state

```yaml
state: 1
attributes:
  prizes:
    - "Straatprijs €25.000"
  period: "05-2026"
```

---

## `sensor.postcodeloterij_<postcode>_last_successful_update`

Diagnostic sensor (hidden in the default dashboard, visible on the device page).

**State:** timestamp of the last successful poll of the lottery API. Updates on every successful refresh even when the prize data is unchanged, so you can alert when the integration goes silently stale — with a 12-hour poll interval that would otherwise take long to notice.

---

## Draw timing

Prizes for month M are published around the 1st of month M+1. The integration always checks the previous month's draw results. Results are fetched every 12 hours — draws only happen once a month, so this is more than sufficient.
