from config import db_config
import psycopg2


def main():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
            CREATE TABLE IF NOT EXISTS stock_delete (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                exchange TEXT NOT NULL,
                get_price_data BOOLEAN NOT NULL 
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS stock_price_delete (
                stock_id INTEGER NOT NULL,
                dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                open NUMERIC (6, 2) NOT NULL, 
                high NUMERIC (6, 2) NOT NULL,
                low NUMERIC (6, 2) NOT NULL,
                close NUMERIC (6, 2) NOT NULL, 
                volume NUMERIC NOT NULL,
                PRIMARY KEY (stock_id, dt),
                CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stock_delete (id)
            )
        """,
        """
            CREATE INDEX IF NOT EXISTS stock_price_delete_idx ON stock_price_delete (stock_id, dt DESC)
        """,
        """
            SELECT create_hypertable('stock_price_delete', 'dt', if_not_exists => TRUE)
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