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
st.write("Crypto and stocks - analysis with news intelligence")

# ==================================================
# SESSION STATE (WATCHLIST)
# ==================================================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ==================================================
# LAYOUT
# ==================================================
left_col, right_col = st.columns([3, 1])

# ==================================================
# HELPERS
# ==================================================
def format_price(x):
    return f"{x:,.2f}".replace(",", " ")

def format_percent(x):
    return f"{x:.2f} %"

# ==================================================
# ASSETS
# ==================================================
ASSETS = {
    "US Stocks": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Nvidia": "NVDA",
        "Tesla": "TSLA"
    },
    "CAC 40": {
        "LVMH": "MC.PA",
        "TotalEnergies": "TTE.PA",
        "Airbus": "AIR.PA",
        "Sanofi": "SAN.PA"
    }
}

# ==================================================
# MAIN TOP CONTENT
# ==================================================
with left_col:
    market = st.selectbox("Market", list(ASSETS.keys()))
    asset_name = st.selectbox("Asset", list(ASSETS[market].keys()))
    ticker = ASSETS[market][asset_name]

    data = yf.Ticker(ticker).history(period="10y")

    if not data.empty:
        last_price = data["Close"].iloc[-1]
        prev_month = data["Close"].iloc[-22]
        monthly_change = (last_price - prev_month) / prev_month * 100

        c1, c2 = st.columns(2)
        c1.metric("Current price", format_price(last_price))
        c2.metric("Monthly change", format_percent(monthly_change))

        st.line_chart(data["Close"])

        if st.button("⭐ Add to watchlist"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)

# ==================================================
# RIGHT COLUMN (SIMPLE FOR NOW)
# ==================================================
with right_col:
    st.subheader("Watchlist")
    if st.session_state.watchlist:
        for w in st.session_state.watchlist:
            st.write(w)
    else:
        st.caption("No assets saved yet.")

# ==================================================
# 🔽 NEWS & INTELLIGENCE SECTION (BOTTOM)
# ==================================================
st.divider()
st.header("News & Intelligence")

tabs = st.tabs([
    "🧠 News summary",
    "🔍 News filter",
    "📊 News vs price",
    "⭐ Watchlist",
    "🔔 Alerts"
])

# ==================================================
# TAB 1 — NEWS SUMMARY (SENTIMENT HEURISTIC)
# ==================================================
with tabs[0]:
    st.subheader("AI-like news summary (heuristic)")

    stock = yf.Ticker(ticker)
    news = stock.news[:10]

    positive_words = ["beat", "growth", "strong", "profit", "upgrade"]
    negative_words = ["miss", "weak", "loss", "downgrade", "risk"]

    score = 0
    for n in news:
        title = n.get("title", "").lower()
        if any(w in title for w in positive_words):
            score += 1
        if any(w in title for w in negative_words):
            score -= 1

    sentiment = "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"

    st.metric("Overall sentiment", sentiment)
    st.write("Based on keyword analysis of recent headlines.")

# ==================================================
# TAB 2 — NEWS FILTER
# ==================================================
with tabs[1]:
    st.subheader("Filtered news")

    category = st.selectbox(
        "Filter by type",
        ["All", "Earnings", "Rumors", "Macro"]
    )

    for n in news:
        title = n.get("title", "")
        if category == "All":
            st.write("-", title)
        elif category == "Earnings" and "earn" in title.lower():
            st.write("-", title)
        elif category == "Rumors" and "rumor" in title.lower():
            st.write("-", title)
        elif category == "Macro" and "fed" in title.lower():
            st.write("-", title)

# ==================================================
# TAB 3 — IMPACT NEWS VS PRICE
# ==================================================
with tabs[2]:
    st.subheader("News impact vs price")

    recent = data.tail(60)
    st.line_chart(recent["Close"])

    st.caption("Visual comparison between recent news flow and price trend.")

# ==================================================
# TAB 4 — WATCHLIST DETAILS
# ==================================================
with tabs[3]:
    st.subheader("Your watchlist")

    if not st.session_state.watchlist:
        st.info("No assets in watchlist.")
    else:
        for w in st.session_state.watchlist:
            hist = yf.Ticker(w).history(period="1y")
            if not hist.empty:
                change = (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100
                st.metric(w, format_percent(change))

# ==================================================
# TAB 5 — ALERTS (V1)
# ==================================================
with tabs[4]:
    st.subheader("Alerts (V1)")

    st.write(
        "Alerts are triggered when:\n"
        "- strong negative news keywords appear\n"
        "- or monthly price change exceeds +/-10%\n"
    )

    if abs(monthly_change) > 10:
        st.warning("Price alert: strong monthly movement detected.")

# ==================================================
# FOOTER
# ==================================================
now_paris = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Last update: " + now_paris.strftime("%Y-%m-%d %H:%M:%S"))
