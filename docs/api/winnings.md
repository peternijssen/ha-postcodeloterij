# POST /public/rest/drawresults/winnings/NPL/P_MT_P{YYYYMM}/

Returns the prize results for a given postcode and monthly draw period.

## Request

**URL:** `https://www.postcodeloterij.nl/public/rest/drawresults/winnings/NPL/P_MT_P{YYYYMM}/?resultSize=10`  
**Method:** `POST`  
**Content-Type:** `application/x-www-form-urlencoded`

### URL parameters

| Parameter | Description |
|-----------|-------------|
| `YYYYMM` | The draw period, e.g. `202604` for April 2026 |
| `resultSize` | Maximum number of results to return. The integration uses `10`. |

### Body

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The postcode to check, e.g. `1234AB` |

### Headers

| Header | Value |
|--------|-------|
| `User-Agent` | A browser user-agent string is required; requests without one may be rejected |

## Response

**Status:** `200 OK` when the draw period exists and the request is valid. A non-200 status or a response body without `prizeCount` indicates the draw for that period has not yet been published.

### Body

```json
{
  "prizeCount": 1,
  "wonPrizes": [
    {
      "code": "7529002",
      "contentId": "a53078f6-5428-4955-915c-baa79975c5c4",
      "description": "Pizzaprijs PL",
      "hasWon": true,
      "key": "1234",
      "labels": [],
      "nrWinningTickets": 0,
      "prizeValue": 3788,
      "publicationDate": "2026-04-30T22:01:00"
    }
  ],
  "enrichedData": [
    {
      "content": "<p>Gefeliciteerd! Je hebt een pizzaprijs gewonnen. Kneden maar, dat deeg! Met een beukenhouten plank, pizzasnijder, pastasaus en kruiden maak je de lekkerste pizza's met eerlijke, Nederlandse ingrediënten. Samen koken, samen genieten. Buon appetito! <a href=\"https://faq.postcodeloterij.nl/topic/cFywPqp8SJJZNLAiq/article/kZB2QmLupm43NuJpj\">Je vindt hier meer informatie over deze prijs &gt;</a></p>\n",
      "contentId": "a53078f6-5428-4955-915c-baa79975c5c4",
      "contentMobile": null,
      "deliveryDateFormat": "d MMMMM",
      "deliveryPeriod": null,
      "deliveryText": null,
      "imgUrl": "https://a.storyblok.com/f/276879/1731957868/201934068vg00000zj8jm.png/m/0x100/filters:quality(90)",
      "lead": null,
      "offsetImgUrl": "https://a.storyblok.com/f/276879/1731957868/201934068vg00000zj8jm.png/m/0x220/filters:quality(90)",
      "prizeIds": null,
      "prizeImgUrl": "https://a.storyblok.com/f/276879/1731957868/201934068vg00000zj8jm.png/m/0x300/filters:quality(90)",
      "prizeTitle": "Pizzaprijs",
      "title": "Pizzaprijs"
    }
  ]
}
```

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `prizeCount` | integer | Number of prizes won. `0` means no prizes for this postcode this period. Used as the sensor state. |
| `wonPrizes` | array | One entry per prize won. Empty when `prizeCount` is `0`. |
| `enrichedData` | array | Richer prize content, linked to `wonPrizes` via `contentId`. Empty when `prizeCount` is `0`. |

### `wonPrizes` object

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Internal prize code |
| `contentId` | string (UUID) | Links this prize to its entry in `enrichedData` |
| `description` | string | Prize name with a lottery-type suffix, e.g. `"Pizzaprijs PL"`. The ` PL` suffix denotes the lottery type and is not shown to users — see `enrichedData[].prizeTitle` instead. |
| `hasWon` | boolean | Always `true` in this response |
| `key` | string | First four digits of the winning postcode |
| `labels` | array | Always observed as empty |
| `nrWinningTickets` | integer | Always observed as `0` |
| `prizeValue` | integer | Prize value in an unspecified unit (observed: `3788`) |
| `publicationDate` | string (ISO 8601) | When the prize result was published |

### `enrichedData` object

| Field | Type | Description |
|-------|------|-------------|
| `content` | string (HTML) | Full prize description as HTML |
| `contentId` | string (UUID) | Links this entry to its `wonPrizes` counterpart |
| `contentMobile` | string\|null | Mobile-specific content. Always `null` in observed data. |
| `deliveryDateFormat` | string | Date format pattern for prize delivery, e.g. `"d MMMMM"` |
| `deliveryPeriod` | string\|null | Delivery period description. `null` in observed data. |
| `deliveryText` | string\|null | Delivery instructions. `null` in observed data. |
| `imgUrl` | string (URL) | Prize image at 100px height |
| `lead` | string\|null | Short lead text. `null` in observed data. |
| `offsetImgUrl` | string (URL) | Prize image at 220px height |
| `prizeIds` | null | Always `null` in observed data |
| `prizeImgUrl` | string (URL) | Prize image at 300px height |
| `prizeTitle` | string | Clean prize name without lottery-type suffix, e.g. `"Pizzaprijs"`. Used by the integration for the `prizes` attribute. |
| `title` | string | Same as `prizeTitle` in observed data |

## How the integration uses this endpoint

- `prizeCount` → sensor state
- `enrichedData[].prizeTitle` → `prizes` attribute (falls back to `wonPrizes[].description` if `enrichedData` is absent)
- The period of the successful response → `period` attribute, formatted as `MM-YYYY`

The integration tries the current calendar month first. If the response is non-200 or lacks `prizeCount`, it retries with the previous month. This handles the window between the 1st of the month and the day the draw results are published.

## Error handling

| Status | Meaning |
|--------|---------|
| `200` | Draw results available for this period |
| `4xx` / `5xx` | Draw not yet published, period invalid, or server error — the integration falls back to the previous month |
