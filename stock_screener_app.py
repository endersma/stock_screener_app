import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Stock Screener", layout="wide")

@st.cache_data
def get_stock_fundamentals(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}/key-statistics"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    data = {'Ticker': ticker}

    stats = {
        'Debt/Equity': 'DEBT_TO_EQUITY-value',
        'Return on Equity (%)': 'RETURN_ON_EQUITY_TTM-value',
        'Profit Margin (%)': 'PROFIT_MARGIN-value',
        '5 Year Revenue Growth Rate (%)': 'FIVE_YEAR_REVENUE_GROWTH_RATE-value',
        'Current Ratio': 'CURRENT_RATIO-value'
    }

    for label, data_test in stats.items():
        element = soup.find('td', {'data-test': data_test})
        data[label] = element.text if element else "N/A"

    return data

def clean_number(val):
    try:
        if isinstance(val, str):
            val = val.replace('%', '').replace(',', '')
        return float(val)
    except:
        return None

def score_company(fundamentals):
    score = 0
    debt_equity = clean_number(fundamentals.get('Debt/Equity'))
    roe = clean_number(fundamentals.get('Return on Equity (%)'))
    profit_margin = clean_number(fundamentals.get('Profit Margin (%)'))
    revenue_growth = clean_number(fundamentals.get('5 Year Revenue Growth Rate (%)'))
    current_ratio = clean_number(fundamentals.get('Current Ratio'))

    if debt_equity is not None and debt_equity < 1.0:
        score += 2
    if roe is not None and roe > 15:
        score += 2
    if profit_margin is not None and profit_margin > 10:
        score += 2
    if revenue_growth is not None and revenue_growth > 5:
        score += 2
    if current_ratio is not None and 1 <= current_ratio <= 2:
        score += 2

    return score

st.title("📈 Stock Screener Dashboard")

tickers_input = st.text_input("Enter stock tickers separated by commas:", "AAPL, TSLA, MSFT, NVDA, AMZN")

if st.button("Analyze Stocks"):
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",")]
    fundamentals_list = []

    for ticker in tickers:
        with st.spinner(f"Fetching {ticker}..."):
            fundamentals = get_stock_fundamentals(ticker)
            if fundamentals:
                fundamentals['Score'] = score_company(fundamentals)
                fundamentals_list.append(fundamentals)

    if fundamentals_list:
        df = pd.DataFrame(fundamentals_list)
        df = df.sort_values(by='Score', ascending=False)

        st.subheader("📊 Screener Results")
        st.dataframe(df)

        st.subheader("🏆 Top 5 Stocks by Score")
        st.bar_chart(df.set_index('Ticker')['Score'].head(5))

        # Save to a shared CSV for other pages
        df.to_csv('screener_data.csv', index=False)

        st.success("Analysis completed!")
    else:
        st.error("No data retrieved.")
