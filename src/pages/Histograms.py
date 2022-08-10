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
        data_complete = pd.read_sql("SELECT * FROM return_histograms", conn)

    pics_per_row = 10
    n_rows = 20
    bins = ['-5 %', '-3.2 %', '-1.6 %', '0 %', '1.6 %', '3.2 %', '5 %']

    # draw the multiplot
    fig = plt.figure(figsize=(pics_per_row * 1.2, n_rows * 1.8))
    for i in range(n_rows * pics_per_row):
        plt.subplot(n_rows, pics_per_row, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)

        hist_str = str(data_complete.iloc[i]['histogram'])
        hist_list = [int(x) for x in hist_str[1:-1].split(',')]
        symbol = data_complete.iloc[i]['symbol']

        plt.bar(x=bins, height=hist_list)
        plt.xlabel(symbol)

    # create streamlit
    st.title("Histograms of the daily returns in percent")
    st.write("The histogram minimum and maximum is +/- 5 percent and it contains 7 bins in total. "
             "The middle bin has approximately +/- 0.8 percent as borders.")
    st.pyplot(fig)


if __name__ == "__main__":
    main()