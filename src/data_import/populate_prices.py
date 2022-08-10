import sys
import config
import json
from datetime import datetime
import time
import aiohttp
import asyncio
import asyncpg


# to avoid the runtime-error
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def write_to_db(connection, params):
    # await connection.copy_records_to_table('stock_price', records=params)

    await connection.executemany("""
        INSERT INTO stock_price_delete (stock_id, dt, open, high, low, close, volume) 
        VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT DO NOTHING 
    """, params)


async def get_price(pool, stock_id, url):
    try:
        async with pool.acquire() as connection:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as response:
                    resp = await response.read()
                    response = json.loads(resp)  # API returns a json file

                    params = [(stock_id,
                               datetime.strptime(entry, "%Y-%m-%d %H:%M:%S"),
                               round(float(response["Time Series (5min)"][entry]["1. open"]), 2),
                               round(float(response["Time Series (5min)"][entry]["2. high"]), 2),
                               round(float(response["Time Series (5min)"][entry]["3. low"]), 2),
                               round(float(response["Time Series (5min)"][entry]["4. close"]), 2),
                               int(response["Time Series (5min)"][entry]["5. volume"])
                               )
                              for entry in response["Time Series (5min)"]]

                    time.sleep(0.5)

                    await write_to_db(connection, params)

    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def get_prices(pool, symbol_urls):
    try:
        # schedule aiohttp requests to run concurrently on all symbols
        ret = await asyncio.gather(*[get_price(pool, stock_id, symbol_urls[stock_id])
                                     for stock_id in symbol_urls])
        print("Finalized all. Returned  list of {} outputs.".format(len(ret)))
    except Exception as e:
        print(e)


async def get_stocks():
    # create database connection pool
    pool = await asyncpg.create_pool(user=config.DB_USER, password=config.DB_PASS,
                                     database=config.DB_NAME,
                                     host=config.DB_HOST, command_timeout=180)
    
    # establish a connection and retrieve the tickers to which price data is to be added
    async with pool.acquire() as connection:
        stocks = await connection.fetch("SELECT * FROM stock_delete WHERE get_price_data=TRUE")

        symbol_urls = {}  # dictionary holding urls
        for stock in stocks:
            symbol_urls[stock['id']] = f"https://www.alphavantage.co/query?function=" \
                                       f"TIME_SERIES_INTRADAY&symbol={stock['symbol']}" \
                                       f"&interval=5min&outputsize=full&apikey={config.API_KEY}"

    await get_prices(pool, symbol_urls)


def main():
    start = time.time()
    asyncio.run(get_stocks())
    end = time.time()
    print("Took {} seconds.".format(end - start))


if __name__ == '__main__':
    main()