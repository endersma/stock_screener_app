import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

st.title("📋 Portfolio / Watchlist Manager")

watchlist_file = "watchlist.csv"
price_history_file = "price_history.csv"

def get_latest_price(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    try:
        price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        price = price_tag.text
        return float(price.replace(',', ''))
    except:
        return None

# Initialize files
if not os.path.exists(watchlist_file):
    pd.DataFrame(columns=["Ticker", "Note"]).to_csv(watchlist_file, index=False)

if not os.path.exists(price_history_file):
    pd.DataFrame(columns=["Timestamp", "Ticker", "Price"]).to_csv(price_history_file, index=False)

# Load files
watchlist_df = pd.read_csv(watchlist_file)
price_history_df = pd.read_csv(price_history_file)

# Add stock
st.subheader("➕ Add a Stock to Watchlist")
new_ticker = st.text_input("Enter a ticker symbol:", "")
new_note = st.text_input("Add a personal note (optional):", "")

if st.button("Add to Watchlist"):
    if new_ticker.strip() != "":
        new_ticker = new_ticker.strip().upper()
        if new_ticker not in watchlist_df['Ticker'].values:
            watchlist_df = watchlist_df.append({"Ticker": new_ticker, "Note": new_note}, ignore_index=True)
            watchlist_df.to_csv(watchlist_file, index=False)
            st.success(f"Added {new_ticker} to watchlist!")
            st.experimental_rerun()
        else:
            st.warning(f"{new_ticker} is already in your watchlist.")

# Remove stock
st.subheader("🗑️ Remove a Stock")
if not watchlist_df.empty:
    selected_to_remove = st.selectbox("Select a stock to remove:", ["None"] + list(watchlist_df['Ticker']))

    if st.button("Remove Selected Stock"):
        if selected_to_remove != "None":
            watchlist_df = watchlist_df[watchlist_df['Ticker'] != selected_to_remove]
            watchlist_df.to_csv(watchlist_file, index=False)
            st.success(f"Removed {selected_to_remove} from watchlist!")
            st.experimental_rerun()

# Live Prices
st.subheader("📈 Live Prices for Watchlist")

if not watchlist_df.empty:
    live_prices = []
    for idx, row in watchlist_df.iterrows():
        ticker = row['Ticker']
        note = row.get('Note', '')
        with st.spinner(f"Fetching price for {ticker}..."):
            price = get_latest_price(ticker)
            live_prices.append({
                "Ticker": ticker,
                "Latest Price": price if price is not None else "N/A",
                "Note": note
            })
            # Save to price history
            if price is not None:
                new_entry = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ticker": ticker,
                    "Price": price
                }
                price_history_df = pd.concat([price_history_df, pd.DataFrame([new_entry])], ignore_index=True)

    # Save updated price history
    price_history_df.to_csv(price_history_file, index=False)

    live_prices_df = pd.DataFrame(live_prices)

    sort_by = st.selectbox("Sort watchlist by:", ["Ticker", "Latest Price"])
    if sort_by == "Ticker":
        live_prices_df = live_prices_df.sort_values(by="Ticker")
    elif sort_by == "Latest Price":
        live_prices_df = live_prices_df.sort_values(by="Latest Price", ascending=False)

    st.dataframe(live_prices_df)
else:
    st.info("Your watchlist is empty. Add some stocks!")
