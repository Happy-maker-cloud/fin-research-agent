import pandas as pd
import pytest

from fin_agent.backtest.momentum import (
    make_demo_prices,
    momentum_factor,
    run_backtest,
)


def test_momentum_formula() -> None:
    prices = pd.DataFrame({"A": [100.0, 110.0, 121.0]})

    result = momentum_factor(prices, lookback=1)

    assert result.iloc[1, 0] == pytest.approx(0.1)
    assert result.iloc[2, 0] == pytest.approx(0.1)


def test_future_price_does_not_change_past_results() -> None:
    prices = make_demo_prices()
    original = run_backtest(prices)

    changed = prices.copy()
    changed.iloc[-1, 0] *= 2
    updated = run_backtest(changed)

    pd.testing.assert_frame_equal(
        original.iloc[:-1],
        updated.iloc[:-1],
    )


def test_cost_reduces_nav() -> None:
    prices = make_demo_prices()

    free = run_backtest(prices, fee_rate=0)
    charged = run_backtest(prices, fee_rate=0.001)

    for name in ("low", "middle", "high", "benchmark"):
        assert (charged[name] <= free[name] + 1e-12).all()


def test_missing_price_is_rejected() -> None:
    prices = make_demo_prices()
    prices.iloc[30, 0] = float("nan")

    with pytest.raises(ValueError, match="缺失值"):
        run_backtest(prices)
