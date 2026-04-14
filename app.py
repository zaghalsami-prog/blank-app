import streamlit as st
import requests
import yfinance as yf
from datetime import datetime

# -----------------------------
# CONFIG GÉNÉRALE
# -----------------------------
st.set_page_config(
    page_title="Crypto & Macro Intelligence",
    layout="wide"
)

st.title("Crypto & Macro Intelligence")
st.caption("Dashboard Python – données quasi temps réel")

# -----------------------------
# FONCTION CRYPTO (CoinGecko)
# -----------------------------
@st.cache_data(ttl=60)
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# -----------------------------
# SECTION CRYPTO
# -----------------------------
st.subheader("🪙 Cryptomonnaies")

try:
    crypto = get_crypto_prices()
    cols = st.columns(len(crypto))

    for col, (name, data) in zip(cols, crypto.items()):
        col.metric(
            label=name.upper(),
            value=f"${data['usd']:,}",
            delta=f"{data['usd_24h_change']:.2f}%"
        )
except Exception as e:
    st.error("Erreur lors du chargement des données crypto.")
    st.exception(e)

# -----------------------------
# SECTION ACTIONS
# -----------------------------
st.subheader("📈 Actions & Indices")

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
            col.write(f"{ticker} : pas assez de données")

    except Exception as e:
        col.error(f"Erreur pour {ticker}")

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.caption(f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
``
