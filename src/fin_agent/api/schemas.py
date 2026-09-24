import re
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class QuoteResponse(BaseModel):
    """单只证券行情响应。"""

    symbol: str
    price: float = Field(gt=0)
    timestamp: datetime


class BatchQuoteRequest(BaseModel):
    """批量行情请求。"""

    symbols: list[str] = Field(min_length=1, max_length=20)

    @field_validator("symbols")
    @classmethod
    def normalize_symbols(cls, symbols: list[str]) -> list[str]:
        normalized_symbols: list[str] = []

        for symbol in symbols:
            normalized = symbol.strip().upper()

            if not re.fullmatch(r"[A-Z0-9.\-]{1,16}", normalized):
                raise ValueError(f"无效的证券代码: {symbol}")

            if normalized not in normalized_symbols:
                normalized_symbols.append(normalized)

        return normalized_symbols


class BatchQuoteResponse(BaseModel):
    """批量行情响应。"""

    count: int
    quotes: list[QuoteResponse]


class ErrorResponse(BaseModel):
    """统一错误响应。"""

    code: str
    message: str
    request_id: str
    details: list[dict[str, Any]] | None = None


class DailyBarResponse(BaseModel):
    symbol: str
    as_of: date
    data_date: date
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    source: str
    retrieved_at: datetime
    cached: bool
