from config import db_config
import psycopg2
import pathlib


def main():
    try:
        # read the connection parameters from config file make config object
        params = db_config.config(ini_file_path='../../config/database.ini')
        # connect to the PostgreSlQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        sql_content = pathlib.Path('commands.sql').read_text(encoding='utf-8')

        sql_statements = sql_content.split(sep=';')

        for statement in sql_statements[:-1]:
            try:
                cur.execute(f'{statement}')
                conn.commit()
            except psycopg2.Error as error_message:
                print(error_message)
                conn.rollback()
        cur.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error_message:
        print(error_message)


if __name__ == '__main__':
    main()