from config import api_config
import sqlalchemy
import datetime
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import streamlit as st
plt.rcParams.update({'figure.max_open_warning': 0})


def plot_bulls(input_date, data_bull, daily_bar, number_x_entries):
    datetime_ob = datetime.datetime(input_date.year, input_date.month, input_date.day)
    datetime_str = str(datetime_ob)

    data_daily_bull = data_bull[data_bull['day'] == datetime_str]
    bulls = data_daily_bull.to_dict('records')

    for i in range(len(bulls)):
        top_data = daily_bar[daily_bar['stock_id'] == bulls[i]['stock_id']]
        top_data = top_data[top_data['day'] <= datetime_str]
        datetime_lower_border = datetime_ob - datetime.timedelta(days=number_x_entries)
        top_data = top_data[top_data['day'] > str(datetime_lower_border)]

        data = top_data.loc[:, ['day', 'open', 'high', 'low', 'close', 'volume']]
        data['date'] = pd.to_datetime(data["day"])

        fig = go.Figure(data=[go.Candlestick(x=data['date'],
                                             open=data['open'],
                                             high=data['high'],
                                             low=data['low'],
                                             close=data['close'])])

        fig.update_xaxes(type='date', tickangle=-90)
        fig.update_layout(height=500,
                          title=str(bulls[i]['symbol']),
                          title_font_size=24,
                          yaxis_title='Price',
                          xaxis_rangeslider_visible=False)

        st.plotly_chart(fig, use_container_width=True)


def plot_threes(input_date, data_three, daily_bar, number_x_entries):
    datetime_ob = datetime.datetime(input_date.year, input_date.month, input_date.day)
    datetime_str = str(datetime_ob)

    data_daily_three = data_three[data_three['day'] == datetime_str]
    threes = data_daily_three.to_dict('records')

    for i in range(len(threes)):
        three_data = daily_bar[daily_bar['stock_id'] == threes[i]['stock_id']]
        three_data = three_data[three_data['day'] <= datetime_str]
        datetime_lower_border = datetime_ob - datetime.timedelta(days=number_x_entries)
        three_data = three_data[three_data['day'] > str(datetime_lower_border)]
        three_data['date'] = pd.to_datetime(three_data['day'])

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=[0.7, 0.2])

        fig.add_trace(go.Candlestick(x=three_data['date'],
                                     open=three_data['open'],
                                     high=three_data['high'],
                                     low=three_data['low'],
                                     close=three_data['close']), row=1, col=1)
        fig.update_traces(showlegend=False)
        fig.update_layout(title=str(threes[i]['symbol']),
                          title_font_size=24,
                          height=700)

        fig.add_trace(go.Bar(x=three_data['date'],
                             y=three_data['volume'],
                             showlegend=False,
                             marker_color='grey'), row=2, col=1)
        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.update_xaxes(type='date', tickangle=-90)

        st.plotly_chart(fig, use_container_width=True)


def main():
    # establish a connection and get dataframes
    conn_url = f'postgresql+psycopg2://{api_config.DB_USER}:{api_config.DB_PASS}' \
               f'@{api_config.DB_HOST}/{api_config.DB_NAME}'

    engine = sqlalchemy.create_engine(conn_url)

    with engine.connect() as conn:
        data_bull_df = pd.read_sql("SELECT * FROM bull", conn)
        data_three_df = pd.read_sql("SELECT * FROM three_bar", conn)
        daily_bar_df = pd.read_sql("SELECT * FROM daily_bars", conn)

    # create streamlit
    st.title("**Pattern Detection**")
    number_x_entries = st.sidebar.number_input("Please enter the number of x-entries (min:0, max:40)",
                                               value=14,
                                               min_value=0,
                                               max_value=40)

    # get time limitations
    time_info = daily_bar_df["day"].agg(["min", "max"])
    time_info_frame = time_info.to_frame()
    min_date = time_info_frame.loc["min"][0].to_pydatetime().date()
    min_date = min_date + datetime.timedelta(days=number_x_entries)
    max_date = time_info_frame.loc["max"][0].to_pydatetime().date()

    i_date = st.sidebar.date_input("Please enter the desired date:",
                                   value=datetime.date(2022, 6, 7),
                                   min_value=min_date,
                                   max_value=max_date)
    st.sidebar.markdown("""
    Sections
    - [Section 1](#section-1)
    - [Section 2](#section-2)
    """, unsafe_allow_html=True)

    st.header('Section 1')
    st.write('Bullish Engulfing')
    plot_bulls(i_date, data_bull_df, daily_bar_df, number_x_entries)
    st.header('Section 2')
    st.write('Triple Closing and Volume Increase')
    plot_threes(i_date, data_three_df, daily_bar_df, number_x_entries)


if __name__ == "__main__":
    main()