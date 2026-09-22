import asyncio
import random
from datetime import UTC, datetime

from fin_agent.exceptions import MarketDataTimeoutError
from fin_agent.models import Quote


async def fetch_quote(symbol: str) -> Quote:
    """模拟异步获取单只股票行情。"""

    try:
        async with asyncio.timeout(2):
            await asyncio.sleep(random.uniform(0.2, 1.0))

            return Quote(
                symbol=symbol,
                price=round(random.uniform(10, 200), 2),
                timestamp=datetime.now(UTC),
            )
    except TimeoutError as exc:
        raise MarketDataTimeoutError(f"获取 {symbol} 行情超时") from exc


async def fetch_quotes(symbols: list[str]) -> list[Quote]:
    """并发获取多只股票行情。"""

    results = await asyncio.gather(*(fetch_quote(symbol) for symbol in symbols))
    return list(results)
