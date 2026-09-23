CREATE TABLE IF NOT EXISTS instruments (
    instrument_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    exchange VARCHAR(32) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, exchange)
);

CREATE TABLE IF NOT EXISTS daily_prices (
    instrument_id BIGINT NOT NULL
        REFERENCES instruments(instrument_id),
    trade_date DATE NOT NULL,
    open_price NUMERIC(20, 6) NOT NULL,
    high_price NUMERIC(20, 6) NOT NULL,
    low_price NUMERIC(20, 6) NOT NULL,
    close_price NUMERIC(20, 6) NOT NULL,
    adjusted_close NUMERIC(20, 6),
    volume BIGINT NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'sample',
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (instrument_id, trade_date),

    CHECK (high_price >= low_price),
    CHECK (volume >= 0)
);

CREATE INDEX IF NOT EXISTS idx_daily_prices_trade_date
    ON daily_prices(trade_date);

CREATE TABLE IF NOT EXISTS financial_facts (
    instrument_id BIGINT NOT NULL
        REFERENCES instruments(instrument_id),
    report_date DATE NOT NULL,
    fiscal_year SMALLINT NOT NULL,
    fiscal_period VARCHAR(10) NOT NULL,
    metric_code VARCHAR(50) NOT NULL,
    metric_value NUMERIC(30, 6) NOT NULL,
    currency CHAR(3),
    unit VARCHAR(20) NOT NULL DEFAULT 'currency',
    source VARCHAR(50) NOT NULL DEFAULT 'sample',
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (
        instrument_id,
        report_date,
        fiscal_period,
        metric_code
    )
);

CREATE INDEX IF NOT EXISTS idx_financial_facts_metric
    ON financial_facts(metric_code);