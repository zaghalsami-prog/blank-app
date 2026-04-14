import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="Crypto Macro Dashboard", layout="wide")

st.title("Crypto Macro Dashboard")
st.write("Analyse base marche crypto et actions")

# -------------------------------
# LAYOUT
# -------------------------------
left_col, right_col = st.columns([3, 1])

# -------------------------------
# DATA CRYPTO TOP 10
# -------------------------------
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

# -------------------------------
# PROJECTION SIMPLE
# -------------------------------
def build_projection(prices):
    df = prices.reset_index()
    df.columns = ["date", "price"]

    df["trend"] = df["price"].rolling(7).mean()

    last_price = df["price"].iloc[-1]
    slope = (df["price"].iloc[-1] - df["price"].iloc[-7]) / 7

    future_dates = pd.date_range(df["date"].iloc[-1], periods=7, freq="D")
    future_prices = [last_price + slope * i for i in range(1, 7)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["price"], name="Prix"))
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_prices,
        name="Projection",
        line=dict(dash="dot")
    ))

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    return fig

# -------------------------------
# MAIN CONTENT
# -------------------------------
with left_col:
    st.subheader("Exemple Bitcoin - projection statistique")

    btc = yf.Ticker("BTC-USD").history(period="90d")
    fig = build_projection(btc["Close"])
    st.plotly_chart(fig, use_container_width=True)

    st.write("Projection basee sur tendance recente. Ce n est pas une prediction.")

# -------------------------------
# RIGHT COLUMN - TOP CAPS
# -------------------------------
with right_col:
    st.subheader("Top capitalisations crypto")

    cryptos = get_top_crypto()

    for c in cryptos:
        change = c.get("price_change_percentage_30d_in_currency", 0)

        st.metric(
            c["name"],
            f"${c['current_price']:,}",
            f"{change:.2f}% sur 30 jours"
        )

# -------------------------------
# FOOTER
# -------------------------------
paris_time = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Derniere mise a jour : " + paris_time.strftime("%d/%m/%Y %H:%M:%S"))
``
