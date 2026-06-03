import os
import time
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Depends, Header
from mangum import Mangum
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="CSS Unit Converter API", version="1.0.0")

# Rate limiting - simple in-memory store
rate_limit_store: Dict[str, list] = {}
RATE_LIMIT = 100  # requests per hour
RATE_WINDOW = 3600  # seconds

# Conversion constants (base values)
PX_PER_INCH = 96  # standard CSS assumption
PX_PER_CM = PX_PER_INCH / 2.54
PX_PER_MM = PX_PER_CM / 10
PX_PER_PC = 16  # picas -> px (1pc = 16px)
PX_PER_PT = PX_PER_PC / 72  # points -> px (1pt = 1/72pc)


def check_rate_limit(api_key: str = None):
    """Simple rate limiting by API key or IP."""
    key = api_key or "anonymous"
    now = time.time()
    if key not in rate_limit_store:
        rate_limit_store[key] = []
    # Clean old entries
    rate_limit_store[key] = [t for t in rate_limit_store[key] if now - t < RATE_WINDOW]
    if len(rate_limit_store[key]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limit_store[key].append(now)


class ConversionRequest(BaseModel):
    value: float
    from_unit: str
    to_unit: str
    base_font_size: float = 16.0  # for rem/em calculations


class ConversionResponse(BaseModel):
    input: Dict[str, Any]
    output: Dict[str, Any]
    converted_value: float


class AllConversionsResponse(BaseModel):
    input: Dict[str, Any]
    conversions: Dict[str, float]


@lru_cache(maxsize=128)
def convert_px_to_unit(px: float, to_unit: str, base_font_size: float) -> float:
    """Convert pixels to any CSS unit."""
    to_unit = to_unit.lower()
    
    if to_unit == "px":
        return px
    elif to_unit == "rem":
        return px / base_font_size
    elif to_unit == "em":
        return px / base_font_size
    elif to_unit == "pt":
        return px / PX_PER_PT
    elif to_unit == "pc":
        return px / PX_PER_PC
    elif to_unit == "in":
        return px / PX_PER_INCH
    elif to_unit == "cm":
        return px / PX_PER_CM
    elif to_unit == "mm":
        return px / PX_PER_MM
    elif to_unit == "vw":
        return px / 100  # relative to viewport width
    elif to_unit == "vh":
        return px / 100  # relative to viewport height
    elif to_unit == "%":
        return px / 100  # percentage (relative context)
    else:
        raise ValueError(f"Unknown unit: {to_unit}")


def convert_to_px(value: float, from_unit: str, base_font_size: float) -> float:
    """Convert any CSS unit to pixels."""
    from_unit = from_unit.lower()
    
    if from_unit == "px":
        return value
    elif from_unit == "rem":
        return value * base_font_size
    elif from_unit == "em":
        return value * base_font_size
    elif from_unit == "pt":
        return value * PX_PER_PT
    elif from_unit == "pc":
        return value * PX_PER_PC
    elif from_unit == "in":
        return value * PX_PER_INCH
    elif from_unit == "cm":
        return value * PX_PER_CM
    elif from_unit == "mm":
        return value * PX_PER_MM
    elif from_unit == "vw":
        return value * 100  # relative to viewport width
    elif from_unit == "vh":
        return value * 100  # relative to viewport height
    elif from_unit == "%":
        return value * 100  # percentage
    else:
        raise ValueError(f"Unknown unit: {from_unit}")


@app.get("/health")
async def health():
    """Health check endpoint - no auth required."""
    return {"status": "ok"}


@app.post("/convert", response_model=ConversionResponse)
async def convert(
    request: ConversionRequest,
    x_api_key: str = Header(None, alias="X-API-Key"),
    _: None = Depends(check_rate_limit)
):
    """Convert a CSS value from one unit to another."""
    try:
        # Convert to pixels first, then to target unit
        px_value = convert_to_px(request.value, request.from_unit, request.base_font_size)
        result = convert_px_to_unit(px_value, request.to_unit, request.base_font_size)
        
        return ConversionResponse(
            input={"value": request.value, "unit": request.from_unit},
            output={"value": round(result, 6), "unit": request.to_unit},
            converted_value=round(result, 6)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/all-conversions", response_model=AllConversionsResponse)
async def all_conversions(
    request: ConversionRequest,
    x_api_key: str = Header(None, alias="X-API-Key"),
    _: None = Depends(check_rate_limit)
):
    """Convert a CSS value to all supported units."""
    units = ["px", "rem", "em", "pt", "pc", "in", "cm", "mm", "vw", "vh", "%"]
    
    try:
        px_value = convert_to_px(request.value, request.from_unit, request.base_font_size)
        conversions = {}
        
        for unit in units:
            if unit == request.from_unit.lower():
                conversions[unit] = request.value
            else:
                conversions[unit] = round(convert_px_to_unit(px_value, unit, request.base_font_size), 6)
        
        return AllConversionsResponse(
            input={"value": request.value, "unit": request.from_unit},
            conversions=conversions
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Legacy Vercel support
handler = Mangum(app)