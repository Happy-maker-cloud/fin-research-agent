import pytest

from fin_agent.analytics.metrics import (
    annualized_volatility,
    information_coefficient,
    max_drawdown,
    sharpe_ratio,
    simple_returns,
    total_return,
)


def test_returns() -> None:
    assert simple_returns([100, 110, 99]) == pytest.approx([0.1, -0.1])
    assert total_return([100, 110, 99]) == pytest.approx(-0.01)


def test_volatility_and_sharpe() -> None:
    # 样本标准差为0.02；用一年4期使计算容易手算。
    returns = [0.01, 0.03, -0.01]

    assert annualized_volatility(returns, 4) == pytest.approx(0.04)
    assert sharpe_ratio(
        returns,
        periods_per_year=4,
    ) == pytest.approx(1.0)


def test_max_drawdown() -> None:
    # 从120下跌到90，回撤25%。
    assert max_drawdown([100, 120, 90, 110]) == pytest.approx(0.25)


def test_ic_and_rank_ic() -> None:
    factors = [1, 2, 3, 4]
    future_returns = [0.01, 0.02, 0.03, 0.04]

    assert information_coefficient(factors, future_returns) == pytest.approx(1.0)

    assert information_coefficient(factors, future_returns, rank=True) == pytest.approx(1.0)


def test_undefined_metrics() -> None:
    assert sharpe_ratio([0.01, 0.01, 0.01]) is None
    assert information_coefficient([1, 1, 1], [0.01, 0.02, 0.03]) is None


def test_invalid_data() -> None:
    with pytest.raises(ValueError):
        simple_returns([100, 0, 110])

    with pytest.raises(ValueError):
        annualized_volatility([0.01, float("nan")])

    with pytest.raises(ValueError):
        information_coefficient([1, 2, 3], [0.01, 0.02, 0.03, 0.04])
