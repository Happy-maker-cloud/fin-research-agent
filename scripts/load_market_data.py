from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from fin_agent.config import settings

CSV_PATH = Path("data/raw/daily_prices_sample.csv")


def load_and_clean_data(path: Path) -> pd.DataFrame:
    """读取并清洗行情数据。"""

    df = pd.read_csv(path, parse_dates=["trade_date"])

    required_columns = {
        "symbol",
        "exchange",
        "company_name",
        "trade_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
        "volume",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"缺少字段: {sorted(missing_columns)}")

    price_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
    ]

    for column in price_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    df["volume"] = pd.to_numeric(
        df["volume"],
        errors="raise",
        downcast="integer",
    )

    df = df.dropna(subset=list(required_columns))
    df = df.drop_duplicates(
        subset=["symbol", "exchange", "trade_date"],
        keep="last",
    )

    df["trade_date"] = df["trade_date"].dt.date

    return df


def save_to_postgres(df: pd.DataFrame) -> None:
    """将清洗后的行情写入 PostgreSQL。"""

    engine = create_engine(settings.database_url)

    instrument_sql = text(
        """
        INSERT INTO instruments (
            symbol,
            exchange,
            company_name
        )
        VALUES (
            :symbol,
            :exchange,
            :company_name
        )
        ON CONFLICT (symbol, exchange)
        DO UPDATE SET company_name = EXCLUDED.company_name
        RETURNING instrument_id
        """
    )

    price_sql = text(
        """
        INSERT INTO daily_prices (
            instrument_id,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            adjusted_close,
            volume
        )
        VALUES (
            :instrument_id,
            :trade_date,
            :open_price,
            :high_price,
            :low_price,
            :close_price,
            :adjusted_close,
            :volume
        )
        ON CONFLICT (instrument_id, trade_date)
        DO UPDATE SET
            open_price = EXCLUDED.open_price,
            high_price = EXCLUDED.high_price,
            low_price = EXCLUDED.low_price,
            close_price = EXCLUDED.close_price,
            adjusted_close = EXCLUDED.adjusted_close,
            volume = EXCLUDED.volume
        """
    )

    with engine.begin() as connection:
        for row in df.to_dict(orient="records"):
            instrument_id = connection.execute(
                instrument_sql,
                row,
            ).scalar_one()

            connection.execute(
                price_sql,
                {
                    **row,
                    "instrument_id": instrument_id,
                },
            )


def main() -> None:
    data = load_and_clean_data(CSV_PATH)
    save_to_postgres(data)
    print(f"成功写入 {len(data)} 条行情数据")


if __name__ == "__main__":
    main()
