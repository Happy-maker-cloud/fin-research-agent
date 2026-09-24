import asyncio
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from time import monotonic

import akshare as ak
import pandas as pd
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from fin_agent.exceptions import MarketDataError
from fin_agent.models import DailyBar

CACHE_TTL_SECONDS = 300
PROVIDER_INTERVAL_SECONDS = 3.0

_provider_lock = asyncio.Lock()
_last_provider_call = 0.0

# 缓存键 -> (过期时间, 数据)
_market_cache: dict[tuple[str, str, str], tuple[float, DailyBar]] = {}


def _make_cache_key(
    symbol: str,
    as_of: date,
    adjust: str,
) -> tuple[str, str, str]:
    return symbol, as_of.isoformat(), adjust


@retry(
    retry=retry_if_exception_type(MarketDataError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
def _download_history(
    symbol: str,
    start_date: str,
    end_date: str,
    adjust: str,
) -> pd.DataFrame:
    try:
        frame = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    except Exception as exc:
        raise MarketDataError(f"AKShare请求失败，symbol={symbol}") from exc

    if frame.empty:
        raise MarketDataError(f"未查询到行情数据，symbol={symbol}")

    return frame


def clear_market_cache() -> None:
    """主要供测试使用。"""
    _market_cache.clear()


async def fetch_daily_bar(
    symbol: str,
    as_of: date,
    adjust: str = "",
) -> DailyBar:
    normalized_symbol = symbol.strip()
    cache_key = _make_cache_key(
        normalized_symbol,
        as_of,
        adjust,
    )

    cached_item = _market_cache.get(cache_key)

    if cached_item is not None:
        expires_at, cached_bar = cached_item

        if monotonic() < expires_at:
            return replace(cached_bar, cached=True)

        del _market_cache[cache_key]

    # 往前查询15天，避免截止日期刚好是周末或节假日
    start_date = as_of - timedelta(days=15)

    global _last_provider_call

    async with _provider_lock:
        elapsed = monotonic() - _last_provider_call
        remaining = PROVIDER_INTERVAL_SECONDS - elapsed

        if remaining > 0:
            await asyncio.sleep(remaining)

        try:
            # AKShare是同步接口，放到线程中运行，避免阻塞FastAPI
            frame = await asyncio.to_thread(
                _download_history,
                normalized_symbol,
                start_date.strftime("%Y%m%d"),
                as_of.strftime("%Y%m%d"),
                adjust,
            )
        finally:
            _last_provider_call = monotonic()

    frame = frame.copy()
    frame["日期"] = pd.to_datetime(frame["日期"]).dt.date
    frame = frame[frame["日期"] <= as_of].sort_values("日期")

    if frame.empty:
        raise MarketDataError(f"截止{as_of}没有可用行情，symbol={normalized_symbol}")

    latest_row = frame.iloc[-1]

    result = DailyBar(
        symbol=normalized_symbol,
        as_of=as_of,
        data_date=latest_row["日期"],
        open=float(latest_row["开盘"]),
        high=float(latest_row["最高"]),
        low=float(latest_row["最低"]),
        close=float(latest_row["收盘"]),
        volume=float(latest_row["成交量"]),
        source="akshare",
        retrieved_at=datetime.now(UTC),
        cached=False,
    )

    _market_cache[cache_key] = (
        monotonic() + CACHE_TTL_SECONDS,
        result,
    )

    return result
