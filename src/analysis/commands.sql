CREATE TABLE IF NOT EXISTS stock_price_impute AS (
    SELECT stock_id,
           time_bucket_gapfill('5 min', dt) AS dt_im,
           interpolate(avg(open)) AS open,
           interpolate(avg(high)) AS high,
           interpolate(avg(low)) AS low,
           interpolate(avg(close)) AS close,
           COALESCE(avg(volume), 0) AS volume
    FROM stock_price_delete
    WHERE dt >= '2022-02-22'
      AND dt < now()
    GROUP BY dt_im, stock_id
);


SELECT create_hypertable(
    'stock_price_impute',
    'dt_im',
    if_not_exists => TRUE,
    migrate_data => true
);


CREATE TABLE IF NOT EXISTS daily_bars_delete AS (
    SELECT stock_id,
           time_bucket(INTERVAL '1 day', dt_im) AS day,
           first(open, dt_im) AS open,
           MAX(high)          AS high,
           MIN(low)           AS low,
           last(close, dt_im) AS close,
           SUM(volume)        AS volume
    FROM stock_price_impute
    GROUP BY stock_id, day
);


CREATE TABLE daily_stock_return_delete AS
    SELECT stock_id, day, open, close, round(-(1-close/open),4) AS intraday_change_in_percent
    FROM daily_bars;


CREATE TABLE return_histograms_delete AS
    SELECT symbol, histogram(intraday_change_in_percent, -0.05, 0.05, 7)
    FROM daily_stock_return_delete JOIN stock
    ON daily_stock_return_delete.stock_id = stock.id
    GROUP BY symbol;
