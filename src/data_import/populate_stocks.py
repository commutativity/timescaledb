from config import db_config
from config import api_config
import csv
import requests
import psycopg2.extras


def main():
    params = db_config.config(ini_file_path='../../config/database.ini')
    connection = psycopg2.connect(**params)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    csv_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_config.API_KEY}'

    with requests.Session() as s:
        download = s.get(csv_url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')

    list_of_lists = list(cr)

    headers = list_of_lists[0]
    list_of_lists.pop(0)

    assets = [dict(zip(headers, sub_list)) for sub_list in list_of_lists]

    for asset in assets:
        print(f"Inserting stock {asset.get('name')} {asset.get('symbol')}")
        cursor.execute("""
            INSERT INTO stock_delete (symbol, name, exchange, get_price_data)
            VALUES (%s, %s, %s, false)
        """, (asset.get('symbol'), asset.get('name'), asset.get('exchange')))

        connection.commit()
        print(asset.get('name'))

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()