from typing import Literal

import numpy as np
import pandas as pd


def clean_daily_data(
    frame: pd.DataFrame,
    trading_dates: list[str],
    adjust: Literal["", "qfq", "hfq"] = "",
) -> pd.DataFrame:
    """清洗单只股票，并对齐指定分析区间的交易日。"""
    required = {"date", "close", "volume"}

    if not required.issubset(frame.columns):
        raise ValueError("缺少date、close或volume列")

    if adjust not in {"", "qfq", "hfq"}:
        raise ValueError("复权方式必须是空字符串、qfq或hfq")

    calendar = pd.DatetimeIndex(pd.to_datetime(trading_dates, errors="raise")).normalize()

    if calendar.empty or calendar.has_duplicates:
        raise ValueError("交易日历不能为空或包含重复日期")

    calendar = calendar.sort_values()
    data = frame.copy()

    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.normalize()

    if data["date"].isna().any():
        raise ValueError("日期不能为空")

    if data["date"].duplicated().any():
        raise ValueError("日期重复，请先检查数据来源")

    if not data["date"].isin(calendar).all():
        raise ValueError("行情日期不在提供的交易日历中")

    data["source_row_present"] = True
    data = data.set_index("date").reindex(calendar)
    data.index.name = "date"

    data["source_row_present"] = data["source_row_present"].eq(True)
    data["missing_row"] = ~data["source_row_present"]

    for column in ("close", "volume"):
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["invalid_price"] = ~np.isfinite(data["close"]) | (data["close"] <= 0)
    data["invalid_volume"] = ~np.isfinite(data["volume"]) | (data["volume"] < 0)

    # 未提供停牌信息时，保留未知，不能猜成False。
    if "suspended" not in data.columns:
        data["suspended"] = pd.Series(pd.NA, index=data.index, dtype="boolean")
    else:
        data["suspended"] = data["suspended"].astype("boolean")

    data["valid_observation"] = (
        ~data["missing_row"] & ~data["invalid_price"] & ~data["invalid_volume"]
    )

    for price_column, flag_column in (
        ("limit_up_price", "at_limit_up_close"),
        ("limit_down_price", "at_limit_down_close"),
    ):
        flags = pd.Series(pd.NA, index=data.index, dtype="boolean")

        if price_column in data.columns:
            if adjust != "":
                raise ValueError("涨跌停判断必须使用不复权价格")

            prices = pd.to_numeric(data[price_column], errors="coerce")
            known = data["valid_observation"] & np.isfinite(prices) & (prices > 0)

            flags.loc[known] = np.isclose(
                data.loc[known, "close"],
                prices.loc[known],
                rtol=0,
                atol=1e-6,
            )

        data[flag_column] = flags

    data["adjust"] = adjust
    return data.reset_index()
