import numpy as np
import pandas as pd

GROUPS = ("low", "middle", "high")  # 分为三个组


def make_demo_prices() -> pd.DataFrame:
    """生成可复现的模拟价格，不代表真实股票行情。"""
    rng = np.random.default_rng(42)

    # 工作日仅用于模拟，不是真实证券交易日历。
    dates = pd.bdate_range("2025-01-01", periods=120)
    symbols = [f"DEMO_{i}" for i in range(6)]

    daily_returns = rng.normal(
        loc=np.linspace(-0.0003, 0.001, 6),
        scale=0.012,
        size=(len(dates), len(symbols)),
    )

    prices = 100 * np.cumprod(1 + daily_returns, axis=0)

    return pd.DataFrame(prices, index=dates, columns=symbols)


def momentum_factor(
    prices: pd.DataFrame,
    lookback: int = 20,
) -> pd.DataFrame:
    if lookback < 1:
        raise ValueError("lookback 必须大于等于 1")

    return prices / prices.shift(lookback) - 1


def run_backtest(
    prices: pd.DataFrame,
    lookback: int = 20,
    fee_rate: float = 0.001,
) -> pd.DataFrame:
    """三组动量回测；费用为买卖成交金额的简化比例费用。"""
    if lookback < 1:
        raise ValueError("lookback 必须大于等于 1")

    if not 0 <= fee_rate < 0.1:
        raise ValueError("fee_rate 必须在 [0, 0.1) 内")

    if prices.shape[1] < 3 or len(prices) < lookback + 4:
        raise ValueError("至少需要 3 只股票和 lookback + 4 行价格")

    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("价格索引必须是 DatetimeIndex")

    if not prices.index.is_unique or not prices.index.is_monotonic_increasing:
        raise ValueError("日期必须唯一并按升序排列")

    if not prices.columns.is_unique:
        raise ValueError("股票代码必须唯一")

    values = prices.to_numpy(dtype=float)

    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("价格必须为有限正数，缺失值需先处理")

    # t-2 日信号，t-1 日收盘调仓，赚取 t-1 到 t 日收益。
    signals = momentum_factor(prices, lookback).shift(2)
    returns = prices.pct_change(fill_method=None)

    first = lookback + 2
    start_date = prices.index[first - 1]
    start_prices = prices.iloc[first - 1]

    nav = dict.fromkeys(GROUPS, 1.0)
    holdings = {name: pd.Series(0.0, index=prices.columns) for name in GROUPS}

    rows = [
        {
            "date": start_date,
            "low": 1.0,
            "middle": 1.0,
            "high": 1.0,
            "benchmark": 1.0,
        }
    ]

    for position in range(first, len(prices)):
        signal = signals.iloc[position]
        daily_return = returns.iloc[position]

        # 相同动量按原列顺序排列，让结果可复现。
        ranked = signal.sort_values(kind="stable").index.tolist()

        # np.array_split 可处理股票数量不能被 3 整除的情况。
        groups = np.array_split(np.array(ranked, dtype=object), 3)

        row = {"date": prices.index[position]}

        for name, members in zip(GROUPS, groups, strict=True):
            target = pd.Series(0.0, index=prices.columns)
            target.loc[members.tolist()] = 1 / len(members)

            # 买入和卖出金额都计入，不除以 2。
            # holdings 是上一期收益发生后漂移的持仓权重。
            traded_fraction = float((target - holdings[name]).abs().sum())
            cost_fraction = fee_rate * traded_fraction

            gross_return = float((target * daily_return).sum())
            net_return = (1 - cost_fraction) * (1 + gross_return) - 1

            nav[name] *= 1 + net_return
            row[name] = nav[name]

            # 价格变化后，持仓权重会发生漂移。
            holdings[name] = target * (1 + daily_return) / (1 + gross_return)

        # 同一股票池初始等权买入并持有，收取一次初始买入费用。
        row["benchmark"] = float((prices.iloc[position] / start_prices).mean() * (1 - fee_rate))

        rows.append(row)

    curves = pd.DataFrame(rows).set_index("date")

    for name in (*GROUPS, "benchmark"):
        # 用正数表示回撤幅度：0.10 表示回撤 10%。
        curves[f"{name}_drawdown"] = 1 - curves[name] / curves[name].cummax()

    return curves


def demo_backtest() -> dict:
    lookback = 20
    fee_rate = 0.001
    curves = run_backtest(make_demo_prices(), lookback, fee_rate)

    summary = {}

    for name in (*GROUPS, "benchmark"):
        daily_returns = curves[name].pct_change().dropna()
        volatility = float(daily_returns.std(ddof=1))

        sharpe = float(daily_returns.mean() / volatility * np.sqrt(252)) if volatility > 0 else None

        summary[name] = {
            "total_return": float(curves[name].iloc[-1] - 1),
            "max_drawdown": float(curves[f"{name}_drawdown"].max()),
            "sharpe": sharpe,
        }

    records = curves.reset_index()
    records["date"] = records["date"].dt.strftime("%Y-%m-%d")

    return {
        "data_source": "synthetic",
        "lookback": lookback,
        "fee_rate": fee_rate,
        "summary": summary,
        "curves": records.to_dict(orient="records"),
    }
