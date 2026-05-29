# Sensors

Full reference for all sensors provided by the Postcodeloterij integration.

## `sensor.postcodeloterij_<postcode>`

One sensor per configured postal code.

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

## Draw timing

Prizes for month M are published around the 1st of month M+1. The integration always checks the previous month's draw results. Results are fetched every 12 hours — draws only happen once a month, so this is more than sufficient.
