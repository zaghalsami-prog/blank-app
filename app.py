import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Market Intelligence Dashboard", layout="wide")

st.title("Market Intelligence Dashboard")
st.write("Crypto & actions – analyse historique et tendances")

# ==================================================
# LAYOUT
# ==================================================
left_col, right_col = st.columns([3, 1])

# ==================================================
# UTIL
# ==================================================
def format_price(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")

def format_percent(x):
    return f"{x:.2f} %"

# ==================================================
# DATA CRYPTO TOP 10
# ==================================================
@st.cache_data(ttl=300)
def get_top_cryptos():
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

# ==================================================
# ACTIONS / INDICES
# ==================================================
ASSETS = {
    "Actions US": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Nvidia": "NVDA",
        "Tesla": "TSLA"
    },
    "CAC 40": {
        "LVMH": "MC.PA",
        "TotalEnergies": "TTE.PA",
        "Airbus": "AIR.PA",
        "Sanofi": "SAN.PA",
        "BNP Paribas": "BNP.PA"
    },
    "Indices": {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "CAC 40 Index": "^FCHI"
    }
}

# ==================================================
# MAIN CONTENT
# ==================================================
with left_col:
    st.subheader("Sélection de l’actif")

    market = st.selectbox("Marché", list(ASSETS.keys()))
    asset_name = st.selectbox("Actif", list(ASSETS[market].keys()))
    ticker = ASSETS[market][asset_name]

    st.subheader(f"{asset_name} – historique 10 ans")

    data = yf.Ticker(ticker).history(period="10y")

    if not data.empty:
        last_price = data["Close"].iloc[-1]
        prev_month = data["Close"].iloc[-22]
        monthly_change = (last_price - prev_month) / prev_month * 100

        col1, col2 = st.columns(2)
        col1.metric("Prix actuel", format_price(last_price))
        col2.metric("Variation 1 mois", format_percent(monthly_change))

        st.line_chart(data["Close"])

    else:
        st.warning("Données indisponibles.")

# ==================================================
# RIGHT COLUMN – TOP CAPITALISATIONS
# ==================================================
with right_col:
    st.subheader("Top capitalisations crypto")

    cryptos = get_top_cryptos()

    for c in cryptos:
        price = c["current_price"]
        change_30d = c.get("price_change_percentage_30d_in_currency", 0)

        signal = "Achat" if change_30d > 0 else "Vente"

        st.metric(
            label=c["name"],
            value=format_price(price),
            delta=f"{format_percent(change_30d)} ({signal})"
        )

# ==================================================
# FOOTER
# ==================================================
now_paris = datetime.now(ZoneInfo("Europe/Paris"))
st.divider()
st.caption("Dernière mise à jour : " + now_paris.strftime("%d/%m/%Y %H:%M:%S"))
``
