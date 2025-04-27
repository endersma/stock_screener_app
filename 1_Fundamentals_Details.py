import streamlit as st
import pandas as pd

st.title("📚 Fundamentals Details")

try:
    df = pd.read_csv('screener_data.csv')
    st.write("Loaded saved screener data!")
except FileNotFoundError:
    st.error("No saved data found. Please run the screener first!")
    st.stop()

selected_ticker = st.selectbox("Select a stock to view full fundamentals:", df['Ticker'])

selected_row = df[df['Ticker'] == selected_ticker]

if not selected_row.empty:
    st.subheader(f"Details for {selected_ticker}")
    st.dataframe(selected_row)
