from config import api_config
import sqlalchemy
import csv
import pandas as pd
import streamlit as st


def get_companies(file_path: str, limit: int) -> list:
    data = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)  # convert to list since csv-object is not subscriptable
        rows.pop(0)
        for row in rows[:limit]:
            data.append(row[2])
    return data


def get_data():
    conn_url = f'postgresql+psycopg2://{api_config.DB_USER}:{api_config.DB_PASS}' \
               f'@{api_config.DB_HOST}/{api_config.DB_NAME}'
    engine = sqlalchemy.create_engine(conn_url)

    with engine.connect() as conn:
        data = pd.read_sql("""SELECT symbol FROM stock""", conn)

    symbol_list = data["symbol"].values.tolist()
    return symbol_list


def ticker_comparison(all_tickers, top_tickers):
    top_tickers_prep = []
    for top_ticker in top_tickers:
        for ticker in all_tickers:
            if top_ticker == ticker:
                top_tickers_prep.append(top_ticker)
            else:
                continue
    return top_tickers_prep


def update_database(tickers):
    conn_url = f'postgresql+psycopg2://{api_config.DB_USER}:{api_config.DB_PASS}' \
               f'@{api_config.DB_HOST}/{api_config.DB_NAME}'
    engine = sqlalchemy.create_engine(conn_url)

    with engine.connect() as conn:
        statement = sqlalchemy.sql.text("UPDATE stock_delete SET get_price_data= CASE "
                                        "WHEN symbol IN :tickers THEN TRUE "
                                        "ELSE FALSE END "
                                        "WHERE id>0")
        print(statement)
        print(tickers)
        conn.execute(statement, tickers=tickers)


def main():
    # create page with information
    url = "https://www.hs-aalen.de/uploads/mediapool/media/file/28860/Logo_HSAA.png"
    st.image(url)
    st.write("**Analysis of Financial Data using TimescaleDB and Visualisation of the Results in a Dashboard**")
    st.write("This website is developed by Daniel Gauermann as part of a project. "
             "The pages Histogram, Simple Moving Average, Daily Winners and Pattern show a "
             "detailed analysis on a stock selection.")

    # fetch the data
    database_symbols = get_data()
    file_path = 'data//us_market_cap.csv'
    top_symbols = get_companies(file_path=file_path, limit=102)
    top_symbols_prep = ticker_comparison(database_symbols, top_symbols)

    # initialize selection
    if "key" not in st.session_state:
        st.session_state["key"] = top_symbols_prep

    selection = st.multiselect("Select tickers:",
                               options=database_symbols,
                               default=st.session_state["key"])

    # update selection and print on dashboard
    save_to_state = st.button("Save & Update")
    if save_to_state:
        st.session_state["key"] = selection
        print(tuple(st.session_state['key']))
        update_database(tuple(st.session_state["key"]))

    # reset the selection to default
    reset_session = st.button("Reset")
    if reset_session:
        st.session_state["key"] = top_symbols_prep

    st.markdown(st.session_state["key"])


if __name__ == "__main__":
    main()