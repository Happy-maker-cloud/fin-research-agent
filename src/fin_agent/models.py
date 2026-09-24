from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Quote:
    """一条股票行情数据。"""

    symbol: str
    price: float
    timestamp: datetime


@dataclass(frozen=True)
class DailyBar:
    symbol: str
    as_of: date
    data_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    retrieved_at: datetime
    cached: bool = False
