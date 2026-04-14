import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Crypto & Macro Intelligence", layout="wide")

# ==================================================
# LAYOUT
# ==================================================
main_col, right_col = st.columns([3, 1])

# ==================================================
# DATA – TOP CRYPTOS
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
    return requests.get(url, params=params).json()

# ==================================================
# DATA – HISTORIQUE PRIX (projection)
# ==================================================
def projection_chart(series, name):
    df = series.reset_index()
    df.columns = ["date", "price"]

    # tendance simple (moyenne mobile)
    df["trend"] = df["price"].rolling(7).mean()

    future_dates = pd.date_range(
        df["date"].iloc[-1],
        periods=7,
        freq="D"
    )

    slope = (df["price"].iloc[-1] - df["price"].iloc[-7]) / 7
    projection = [df["price"].iloc[-1] + slope * i for i in range(1, 7)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["price"],
        name="Prix réel"
    ))

    fig.add_trace(go.Scatter(
        x=future_dates,
        y=projection,
        name="Projection (indicative)",
        line=dict(dash="dot")
    ))

    fig.update_layout(
        title=name,
        height=250,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    return fig

# ==================================================
# MAIN CONTENT
# ==================================================
with main_col:
    st.title("Crypto & Macro Intelligence")
    st.caption("Analyse des marchés – données réelles")

    st.subheader("📊 Exemple projection – Bitcoin")

    btc = yf.Ticker("BTC-USD").history(period="90d")
    fig = projection_chart(btc["Close"], "Bitcoin – projection statistique")
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Projection basée sur tendance historique et moyenne mobile. "
        "Ce n’est pas une prédiction de marché."
    )

# ==================================================
# RIGHT SIDEBAR – TOP CAPITALISATIONS
# ==================================================
with right_col:
    st.subheader("🔝 Top Capitalisations")

    cryptos = get_top_cryptos()

    for c in cryptos:
        variation = c.get("price_change_percentage_30d_in_currency", 0)

        st.metric(
            label=f"{c['name']} ({c['symbol'].upper()})",
            value=f"${c['current_price']:,}",
            delta=f"{variation:.2f}% / 30j"
        )

    st.divider()

    st.caption("Signal indicatif :")
    st.markdown("""
    - 📈 Hausse mensuelle → pression acheteuse  
    - 📉 Baisse mensuelle → pression vendeuse  
    """)

# ==================================================
# FOOTER
# ==================================================
paris_time = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Mise à jour : " + paris_time.strftime("%d/%m/%Y %H:%M:%S"))
``
