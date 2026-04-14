import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(page_title="Market Dashboard", layout="wide")

st.title("Market Dashboard")
st.write("Crypto and stock overview")

# ------------------------------
# LAYOUT
# ------------------------------
left_col, right_col = st.columns([3, 1])

# ------------------------------
# CRYPTO TOP 10
# ------------------------------
@st.cache_data(ttl=300)
def get_top_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "price_change_percentage": "30d"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# ------------------------------
# MAIN CONTENT
# ------------------------------
with left_col:
    st.subheader("Bitcoin price (last 90 days)")

    btc = yf.Ticker("BTC-USD").history(period="90d")
    st.line_chart(btc["Close"])

# ------------------------------
# RIGHT COLUMN
# ------------------------------
with right_col:
    st.subheader("Top crypto by market cap")

    cryptos = get_top_crypto()

    for c in cryptos:
        change = c.get("price_change_percentage_30d_in_currency", 0)

        st.metric(
            label=c["name"],
            value=str(c["current_price"]),
            delta=str(round(change, 2)) + "% (30d)"
        )

# ------------------------------
# FOOTER
# ------------------------------
now_paris = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Last update: " + now_paris.strftime("%Y-%m-%d %H:%M:%S"))
