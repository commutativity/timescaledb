from config import api_config
import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def main():
    # establish a connection and get dataframes
    conn_url = f'postgresql+psycopg2://{api_config.DB_USER}:{api_config.DB_PASS}' \
               f'@{api_config.DB_HOST}/{api_config.DB_NAME}'

    engine = sqlalchemy.create_engine(conn_url)

    with engine.connect() as conn:
        data_complete = pd.read_sql("SELECT * FROM sma_14", conn)

    pics_per_row = 10
    n_rows = 20

    symbols = data_complete["symbol"].unique()
    fig = plt.figure(figsize=(pics_per_row * 1.2, n_rows * 1.8))

    # draw the multiplot
    for i, symbol in zip(range(n_rows * pics_per_row), symbols):
        data_single_stock = data_complete[data_complete["symbol"] == symbol]
        day = pd.to_datetime(data_single_stock["day"])
        close = data_single_stock["close"]
        sma_14 = data_single_stock["sma_14"]

        plt.subplot(n_rows, pics_per_row, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)

        plt.plot(day, close)
        plt.plot(day, sma_14)
        plt.xlabel(symbol)

    # create streamlit
    st.title("Closing Prices and SMA 14")
    st.write("SMA 14 is Simple Moving Average over the last 14 entries (current day and previous 13 days).")
    st.pyplot(fig)


if __name__ == "__main__":
    main()