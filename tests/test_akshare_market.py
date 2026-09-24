import asyncio
from datetime import date

import pandas as pd

from fin_agent.services import akshare_market


def test_fetch_daily_bar_uses_date_cutoff_and_cache(
    monkeypatch,
) -> None:
    call_count = 0

    def fake_download(
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str,
    ) -> pd.DataFrame:
        nonlocal call_count
        call_count += 1

        return pd.DataFrame(
            {
                "日期": [
                    "2026-09-22",
                    "2026-09-23",
                    "2026-09-24",
                ],
                "开盘": [10.0, 11.0, 12.0],
                "最高": [10.5, 11.5, 12.5],
                "最低": [9.8, 10.8, 11.8],
                "收盘": [10.2, 11.2, 12.2],
                "成交量": [1000, 2000, 3000],
            }
        )

    akshare_market.clear_market_cache()

    monkeypatch.setattr(
        akshare_market,
        "_download_history",
        fake_download,
    )

    first_result = asyncio.run(
        akshare_market.fetch_daily_bar(
            symbol="000001",
            as_of=date(2026, 9, 23),
        )
    )

    second_result = asyncio.run(
        akshare_market.fetch_daily_bar(
            symbol="000001",
            as_of=date(2026, 9, 23),
        )
    )

    assert first_result.data_date == date(2026, 9, 23)
    assert first_result.close == 11.2
    assert first_result.cached is False

    assert second_result.cached is True
    assert call_count == 1
