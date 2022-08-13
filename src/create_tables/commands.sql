DROP TABLE IF EXISTS stock_delete CASCADE;
CREATE TABLE stock_delete (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    exchange TEXT NOT NULL,
    get_price_data BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS stock_price_delete;
CREATE TABLE stock_price_delete (
    stock_id INTEGER NOT NULL,
    dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    open NUMERIC (6, 2) NOT NULL,
    high NUMERIC (6, 2) NOT NULL,
    low NUMERIC (6, 2) NOT NULL,
    close NUMERIC (6, 2) NOT NULL,
    volume NUMERIC NOT NULL,
    PRIMARY KEY (stock_id, dt),
    CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stock_delete (id)
);

CREATE INDEX IF NOT EXISTS stock_price_delete_idx ON stock_price_delete (stock_id, dt DESC);

SELECT create_hypertable('stock_price_delete', 'dt', if_not_exists => TRUE);