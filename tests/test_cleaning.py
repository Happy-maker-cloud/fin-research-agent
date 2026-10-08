import pandas as pd
import pytest

from fin_agent.data.cleaning import clean_daily_data


def test_align_calendar_without_filling_price() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-04"],
            "close": [10.0, 11.0],
            "volume": [100, 200],
        }
    )

    result = clean_daily_data(
        frame,
        ["2024-01-02", "2024-01-03", "2024-01-04"],
    )

    assert len(result) == 3
    assert bool(result.loc[1, "missing_row"])
    assert pd.isna(result.loc[1, "close"])
    assert pd.isna(result.loc[1, "suspended"])


def test_suspension_and_limit_flags() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03"],
            "close": [11.0, 11.0],
            "volume": [100, 0],
            "suspended": [False, True],
            "limit_up_price": [11.0, None],
            "limit_down_price": [9.0, None],
        }
    )

    result = clean_daily_data(frame, ["2024-01-02", "2024-01-03"])

    assert bool(result.loc[0, "at_limit_up_close"])
    assert not bool(result.loc[0, "at_limit_down_close"])
    assert bool(result.loc[1, "suspended"])


def test_invalid_price() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-02"],
            "close": [0],
            "volume": [100],
        }
    )

    result = clean_daily_data(frame, ["2024-01-02"])

    assert bool(result.loc[0, "invalid_price"])
    assert not bool(result.loc[0, "valid_observation"])


def test_duplicate_dates() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-02"],
            "close": [10, 11],
            "volume": [100, 200],
        }
    )

    with pytest.raises(ValueError):
        clean_daily_data(frame, ["2024-01-02"])


def test_adjusted_price_cannot_compare_with_limit_price() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-02"],
            "close": [8],
            "volume": [100],
            "limit_up_price": [11],
        }
    )

    with pytest.raises(ValueError):
        clean_daily_data(frame, ["2024-01-02"], adjust="qfq")
