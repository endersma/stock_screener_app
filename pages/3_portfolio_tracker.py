import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Portfolio Price Tracker")

price_history_file = "price_history.csv"

try:
    history_df = pd.read_csv(price_history_file)
    history_df['Timestamp'] = pd.to_datetime(history_df['Timestamp'])
except FileNotFoundError:
    st.error("No price history found. Fetch some live prices first!")
    st.stop()

tickers = history_df['Ticker'].unique()

selected_ticker = st.selectbox("Select a stock to view price trend:", tickers)

ticker_df = history_df[history_df['Ticker'] == selected_ticker].sort_values('Timestamp')

if not ticker_df.empty:
    st.line_chart(data=ticker_df.set_index('Timestamp')['Price'])
else:
    st.warning("No price data available for this stock.")
