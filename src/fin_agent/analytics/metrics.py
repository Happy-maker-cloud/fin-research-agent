import numpy as np
from scipy.stats import pearsonr, spearmanr


def _array(values: list[float], minimum: int = 2) -> np.ndarray:
    result = np.asarray(values, dtype=float)

    if result.ndim != 1 or result.size < minimum:
        raise ValueError(f"需要至少{minimum}个一维数据")

    if not np.isfinite(result).all():
        raise ValueError("数据不能包含NaN或无穷值")

    return result


def _periods(periods_per_year: int) -> None:
    if periods_per_year <= 0:
        raise ValueError("年化期数必须为正数")


def simple_returns(prices: list[float]) -> list[float]:
    """价格转换为逐期简单收益率。"""
    values = _array(prices)

    if np.any(values <= 0):
        raise ValueError("价格必须大于0")

    returns = values[1:] / values[:-1] - 1
    return returns.tolist()


def total_return(prices: list[float]) -> float:
    """首尾价格计算累计收益率。"""
    values = _array(prices)

    if np.any(values <= 0):
        raise ValueError("价格必须大于0")

    return float(values[-1] / values[0] - 1)


def annualized_volatility(
    returns: list[float],
    periods_per_year: int = 252,
) -> float:
    values = _array(returns)
    _periods(periods_per_year)

    return float(values.std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(
    returns: list[float],
    annual_risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float | None:
    values = _array(returns)
    _periods(periods_per_year)

    if not np.isfinite(annual_risk_free_rate) or annual_risk_free_rate <= -1:
        raise ValueError("年无风险利率必须有限且大于-1")

    # 将年无风险利率转换成单期利率。
    periodic_rf = (1 + annual_risk_free_rate) ** (1 / periods_per_year) - 1
    excess_returns = values - periodic_rf
    std = float(excess_returns.std(ddof=1))

    if std <= 1e-12:
        return None

    return float(excess_returns.mean() / std * np.sqrt(periods_per_year))


def max_drawdown(equity: list[float]) -> float:
    """输入按时间排列的账户净值，返回正数形式的最大回撤。"""
    values = _array(equity)

    if np.any(values <= 0):
        raise ValueError("本练习要求账户净值大于0")

    running_peak = np.maximum.accumulate(values)
    drawdowns = 1 - values / running_peak

    return float(drawdowns.max())


def information_coefficient(
    factor_values: list[float],
    forward_returns: list[float],
    rank: bool = False,
) -> float | None:
    factors = _array(factor_values, minimum=3)
    returns = _array(forward_returns, minimum=3)

    if factors.size != returns.size:
        raise ValueError("因子值与未来收益长度必须一致")

    if np.all(factors == factors[0]) or np.all(returns == returns[0]):
        return None

    result = spearmanr(factors, returns) if rank else pearsonr(factors, returns)
    coefficient = float(result.statistic)

    return coefficient if np.isfinite(coefficient) else None
