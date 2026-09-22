from dataclasses import dataclass
from datetime import datetime


@dataclass
class Quote:
    """一条股票行情数据。"""

    symbol: str
    price: float
    timestamp: datetime
