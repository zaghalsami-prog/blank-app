import streamlit as st
import requests
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

# ==================================================
# CONFIGURATION GÉNÉRALE
# ==================================================
st.set_page_config(
    page_title="Crypto & Macro Intelligence",
    layout="wide"
)

st.title("Crypto & Macro Intelligence")
st.caption("Dashboard Python – données quasi temps réel")

# ==================================================
# CRYPTOS – COINGECKO
# ==================================================
@st.cache_data(ttl=60)
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

st.subheader("🪙 Cryptos")

try:
    crypto = get_crypto_prices()
    cols = st.columns(len(crypto))

    for col, (name, data) in zip(cols, crypto.items()):
        col.metric(
            label=name.upper(),
            value=f"${data['usd']:,}",
            delta=f"{data['usd_24h_change']:.2f}%"
        )
except Exception:
    st.error("Erreur lors du chargement des données crypto.")

# ==================================================
# ACTIONS – YAHOO FINANCE
# ==================================================
st.subheader("📈 Actions")

tickers = ["AAPL", "MSFT", "NVDA", "^GSPC"]
cols = st.columns(len(tickers))

for col, ticker in zip(cols, tickers):
    try:
        hist = yf.Ticker(ticker).history(period="5d")

        if len(hist) >= 2:
            price = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2]
            delta = (price - prev) / prev * 100

            col.metric(
                label=ticker,
                value=f"${price:.2f}",
                delta=f"{delta:.2f}%"
            )
        else:
            col.write("Données insuffisantes")

    except Exception:
        col.error("Erreur de chargement")

# ==================================================
# FOOTER – HEURE FRANCE
# ==================================================
st.divider()
paris_time = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Mise à jour : " + paris_time.strftime("%d/%m/%Y %H:%M:%S"))
