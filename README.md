# CSS Unit Converter API

A simple API to convert between CSS units (px, rem, em, pt, pc, in, cm, mm, vw, vh, %).

## Endpoints

### `GET /health`
Health check endpoint. No API key required.

### `POST /convert`
Convert a CSS value from one unit to another.

**Request Body:**
```json
{
  "value": 16,
  "from_unit": "px",
  "to_unit": "rem",
  "base_font_size": 16
}
```

**Response:**
```json
{
  "input": {"value": 16, "unit": "px"},
  "output": {"value": 1, "unit": "rem"},
  "converted_value": 1
}
```

### `POST /all-conversions`
Convert a CSS value to all supported units.

**Request Body:**
```json
{
  "value": 16,
  "from_unit": "px",
  "base_font_size": 16
}
```

**Response:**
```json
{
  "input": {"value": 16, "unit": "px"},
  "conversions": {
    "px": 16,
    "rem": 1,
    "em": 1,
    "pt": 12,
    "pc": 1.041667,
    "in": 0.166667,
    "cm": 0.423333,
    "mm": 4.233333,
    "vw": 16,
    "vh": 16,
    "%": 16
  }
}
```

## Authentication

Include `X-API-Key` header with any value to authenticate. Rate limit: 100 requests per hour per key.

## Examples

```bash
# Convert px to rem
curl -X POST https://css-unit-converter.vercel.app/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo" \
  -d '{"value": 16, "from_unit": "px", "to_unit": "rem"}'

# Get all conversions for a value
curl -X POST https://css-unit-converter.vercel.app/all-conversions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo" \
  -d '{"value": 2, "from_unit": "rem"}'
```

## Pricing

Available on RapidAPI for $19/month for teams needing production-grade conversions.

## Postman
[![Run in Postman](https://run.pstmn.io/button.svg)](https://raw.githubusercontent.com/BT-Builds/css-unit-converter/main/postman_collection.json)
