from datetime import datetime
import streamlit as st
import requests
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Crypto & Macro Intelligence", layout="wide")

st.title("Crypto & Macro Intelligence")
st.caption("Dashboard Python – données quasi temps réel")

@st.cache_data(ttl=60)
def get_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    return requests.get(url, params=params).json()

st.subheader("🪙 Cryptos")

crypto = get_crypto()
cols = st.columns(len(crypto))

for col, (name, data) in zip(cols, crypto.items()):
    col.metric(
        name.upper(),
        f"${data['usd']:,}",
        f"{data['usd_24h_change']:.2f}%"
    )

st.subheader("📈 Actions")

tickers = ["AAPL", "MSFT", "NVDA", "^GSPC"]
cols = st.columns(len(tickers))

for col, ticker in zip(cols, tickers):
    hist = yf.Ticker(ticker).history(period="5d")

    if len(hist) >= 2:
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        delta = (price - prev) / prev * 100

        col.metric(ticker, f"${price:.2f}", f"{delta:.2f}%")

st.caption("Mise à jour : " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
