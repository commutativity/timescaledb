from config import db_config
import psycopg2


def main():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
            CREATE TABLE IF NOT EXISTS stock_price_delete_impute AS (
                SELECT
                    stock_id,
                    time_bucket_gapfill('5 min', dt) AS dt,
                    interpolate(avg(open)) AS open,
                    interpolate(avg(high)) AS high,
                    interpolate(avg(low)) AS low,
                    interpolate(avg(close)) AS close,
                    COALESCE(avg(volume), 0) AS volume
                FROM stock_price_delete
                WHERE dt >= '2022-02-22' AND dt < now()
                GROUP BY dt, stock_id
            )
        """,
        """
            CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_bars_delete
            WITH (timescaledb.continuous) AS
            SELECT stock_id,
                   time_bucket(INTERVAL '1 hour', dt) AS day,
                   first(open, dt) as open,
                   MAX(high) as high,
                   MIN(low) as low,
                   last(close, dt) as close,
                   SUM(volume) as volume
            FROM stock_price_delete_impute
            GROUP BY stock_id, day
        """)
    conn = None
    try:
        # read the connection parameters from config file make config object
        params = db_config.config(ini_file_path='../../config/database.ini')
        # connect to the PostgreSlQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    main()