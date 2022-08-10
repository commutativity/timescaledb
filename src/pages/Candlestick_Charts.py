from config import api_config
import sqlalchemy
import pandas as pd
import streamlit as st
import plotly.graph_objs as go


def main():
    # get a connection to the database
    conn_url = f'postgresql+psycopg2://{api_config.DB_USER}:{api_config.DB_PASS}' \
               f'@{api_config.DB_HOST}/{api_config.DB_NAME}'
    engine = sqlalchemy.create_engine(conn_url)

    # streamlit user input
    symbol = st.sidebar.text_input("Symbol", value='MSFT', max_chars=None, key=None, type='default')

    # get data and draw visualization
    with engine.connect() as conn:
        data = pd.read_sql("""
            select date(day) as day, open, high, low, close
            from daily_bars
            where stock_id = (select id from stock where UPPER(symbol) = %s) 
            order by day asc""", conn, params=(symbol.upper(),))

    fig = go.Figure(data=[go.Candlestick(x=data['day'],
                                         open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'])])

    fig.update_xaxes(type='date', tickangle=-90)
    fig.update_layout(height=700,
                      title=symbol.upper(),
                      title_font_size=20,
                      shapes=[dict(x0='2022-03-22', x1='2022-03-22',
                                   y0=0, y1=1, xref='x', yref='paper', line_width=0.5)],
                      annotations=[dict(x='2022-03-22', y=0.05, xref='x', yref='paper',
                                        showarrow=False, xanchor='left', text='Data Imputation')],
                      yaxis_title='Price')
    st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    main()