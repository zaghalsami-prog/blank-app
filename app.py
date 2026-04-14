import streamlit as st
import requests
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Crypto & Macro Intelligence", layout="wide")

st.title("Crypto & Macro Intelligence")
st.caption("Dashboard Python – cryptos & actions multi‑marchés")

# ==================================================
# CRYPTOS – COINGECKO
# ==================================================
@st.cache_data(ttl=3600)
def get_all_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/list"
    return requests.get(url, timeout=10).json()

@st.cache_data(ttl=60)
def get_crypto_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    return requests.get(url, params=params, timeout=10).json()

st.subheader("🪙 Cryptomonnaies")

cryptos = get_all_cryptos()
crypto_names = {c["name"]: c["id"] for c in cryptos}

selected_crypto = st.selectbox(
    "Choisis une crypto",
    options=sorted(crypto_names.keys()),
    index=sorted(crypto_names.keys()).index("Bitcoin")
)

crypto_data = get_crypto_price(crypto_names[selected_crypto])

if selected_crypto.lower() in crypto_data:
    data = crypto_data[crypto_names[selected_crypto]]
    st.metric(
        label=selected_crypto,
        value=f"${data['usd']:,}",
        delta=f"{data['usd_24h_change']:.2f}%"
    )

# ==================================================
# ACTIONS – MULTI MARCHÉS
# ==================================================
st.subheader("📈 Actions & Indices")

MARKETS = {
    "🇺🇸 États‑Unis": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Nvidia": "NVDA",
        "Tesla": "TSLA"
    },
    "🇪🇺 Europe": {
        "LVMH": "MC.PA",
        "TotalEnergies": "TTE.PA",
        "Airbus": "AIR.PA",
        "Sanofi": "SAN.PA"
    },
    "📊 Indices": {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "CAC 40": "^FCHI",
        "DAX": "^GDAXI"
    }
}

selected_market = st.selectbox(
    "Choisis un marché",
    list(MARKETS.keys())
)

selected_stock = st.selectbox(
    "Choisis une action",
    list(MARKETS[selected_market].keys())
)

ticker = MARKETS[selected_market][selected_stock]

try:
    hist = yf.Ticker(ticker).history(period="5d")

    if len(hist) >= 2:
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        delta = (price - prev) / prev * 100

        st.metric(
            label=f"{selected_stock} ({ticker})",
            value=f"${price:.2f}",
            delta=f"{delta:.2f}%"
        )
except Exception:
    st.error("Erreur de chargement des données actions.")

# ==================================================
# FOOTER – HEURE FRANCE
# ==================================================
st.divider()
paris_time = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Mise à jour : " + paris_time.strftime("%d/%m/%Y %H:%M:%S"))
