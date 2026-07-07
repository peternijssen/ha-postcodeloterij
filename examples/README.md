# Examples

Ready-to-paste Home Assistant snippets for the Postcodeloterij integration.

| Folder | Contents |
|---|---|
| [`automations/`](automations/) | YAML automation snippets — copy them into your `automations.yaml` or paste them into the Automation editor in **raw editor** mode. |
| [`dashboards/`](dashboards/) | Lovelace dashboard card snippets — paste them into the YAML editor of any card. |

The examples use `sensor.postcodeloterij_1234ab_prizes`. Replace `1234ab`
with your own postcode (lowercase, as HA generates it). Installations that
existed before the entity was renamed keep the older id
`sensor.postcodeloterij_1234ab` (without the `_prizes` suffix) — adjust
accordingly.
