from config import api_config
import sqlalchemy
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import streamlit as st


def plot_winners(data_daily, datetime_str, limit, pics_per_row, n_rows, daily_bar):
    data_daily_max = data_daily[data_daily['day'] == datetime_str][1:]  # omit first entry
    data_daily_max = data_daily_max[:limit]
    top_stocks = data_daily_max.to_dict('records')

    fig = plt.figure(figsize=(pics_per_row * 5, n_rows * 7))

    color = cm.RdYlGn(np.linspace(1, 0.6, limit))
    for i, col in zip(range(limit), color):
        plt.subplot(n_rows, pics_per_row, i+1)

        top_data = daily_bar[daily_bar['stock_id'] == top_stocks[i]['stock_id']]
        top_data = top_data[top_data['day'] <= datetime_str]
        day = pd.to_datetime(top_data['day'])
        close = top_data['close']
        close_star = top_data['close'][:-2]
        day_star = pd.to_datetime(top_data['day'][:-2])
        label = str(top_stocks[i]['symbol']) + " (" + str(top_stocks[i]['max_daily_factor']) + ")"

        plt.fill_between(day, close, color=col)
        plt.fill_between(day_star, close_star, color='lightblue')
        plt.yticks()
        plt.xticks(rotation=30)
        plt.grid(True)
        plt.xlabel(label, fontsize=14)

    st.write("Daily winners")
    st.pyplot(fig)


def plot_losers(data_daily, datetime_str, limit, pics_per_row, n_rows, daily_bar):
    data_daily_min = data_daily[data_daily['day'] == datetime_str][1:]
    data_daily_min = data_daily_min.tail(limit)
    flop_stocks = data_daily_min.to_dict('records')

    fig = plt.figure(figsize=(pics_per_row * 5, n_rows * 7))

    color = cm.RdYlGn(np.linspace(0, 0.4, limit))
    for i, col in zip(range(limit), color):
        plt.subplot(n_rows, pics_per_row, i+1)

        # access flop_stocks in reverse order
        flop_data = daily_bar[daily_bar['stock_id'] == flop_stocks[-i-1]['stock_id']]
        flop_data = flop_data[flop_data['day'] <= datetime_str]
        day = pd.to_datetime(flop_data['day'])
        close = flop_data['close']
        close_star = flop_data['close'][:-2]
        day_star = pd.to_datetime(flop_data['day'][:-2])
        label = str(flop_stocks[-i-1]['symbol']) + " (" + str(flop_stocks[-i-1]['max_daily_factor']) + ")"

        plt.fill_between(day, close, color=col)
        plt.fill_between(day_star, close_star, color='lightblue')
        plt.yticks()
        plt.xticks(rotation=30)
        plt.grid(True)
        plt.xlabel(label, fontsize=14)

    st.write("Daily losers")
    st.pyplot(fig)


def main():
    # establish connection
    conn_url = f'postgresql+psycopg2://{api_config.DB_USER}:{api_config.DB_PASS}' \
               f'@{api_config.DB_HOST}/{api_config.DB_NAME}'

    engine = sqlalchemy.create_engine(conn_url)

    with engine.connect() as conn:
        data_daily = pd.read_sql("SELECT * FROM daily_max", conn)
        daily_bar = pd.read_sql("SELECT * FROM daily_bars", conn)

    # get time limitations
    time_info = daily_bar["day"].agg(["min", "max"])
    time_info_frame = time_info.to_frame()
    min_date = time_info_frame.loc["min"][0].to_pydatetime().date()
    max_date = time_info_frame.loc["max"][0].to_pydatetime().date()

    # create streamlit
    st.title("Daily winners and losers")
    st.write("**Overview of daily winners and losers. The parenthesis contains the daily factor.**")
    input_date = st.sidebar.date_input("Please enter date",
                                       value=datetime.date(2022, 6, 7),
                                       min_value=min_date,
                                       max_value=max_date)
    limit = st.sidebar.slider(label='Number of results', min_value=4, max_value=100, value=4, step=4)

    pics_per_row = 4
    n_rows = 40
    datetime_str = str(input_date) + ' 00:00:00'
    plot_winners(data_daily, datetime_str, limit, pics_per_row, n_rows, daily_bar)
    plot_losers(data_daily, datetime_str, limit, pics_per_row, n_rows, daily_bar)


if __name__ == "__main__":
    main()