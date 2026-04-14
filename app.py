import streamlit as st
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

# ==================================================
# CONFIG
# ==================================================
st.set_page_config(page_title="Market Intelligence Dashboard", layout="wide")
st.title("Market Intelligence Dashboard")
st.write("Crypto and stocks - analysis with news intelligence")

# ==================================================
# SESSION STATE
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
    try:
        return f"{x:,.2f}".replace(",", " ")
    except Exception:
        return "-"

def format_percent(x):
    try:
        return f"{x:.2f} %"
    except Exception:
        return "-"

@st.cache_data(ttl=300)
def get_history(ticker):
    try:
        data = yf.Ticker(ticker).history(period="10y")
        return data
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.news[:10] if stock.news else []
    except Exception:
        return []

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
# MAIN CONTENT (TOP)
# ==================================================
with left_col:
    st.subheader("Asset selection")

    market = st.selectbox("Market", list(ASSETS.keys()))
    asset_name = st.selectbox("Asset", list(ASSETS[market].keys()))
    ticker = ASSETS[market][asset_name]

    st.markdown("### Or search any stock by ticker")

    custom_ticker = st.text_input(
        "Enter a Yahoo Finance ticker",
        placeholder="Examples: ASML.AS, NFLX, OR.PA, SAP.DE"
    )

    if custom_ticker:
        ticker = custom_ticker.upper()

    # ------------------------------
    # PRICE DATA
    # ------------------------------
    data = get_history(ticker)

    if data is None:
        st.error("Données indisponibles (rate limit Yahoo Finance). Réessaie dans 1 minute.")
        st.stop()
    elif data.empty or len(data) <= 22:
        st.warning("Not enough historical data available.")
    else:
        last_price = data["Close"].iloc[-1]
        prev_month = data["Close"].iloc[-22]
        monthly_change = (last_price - prev_month) / prev_month * 100

        c1, c2 = st.columns(2)
        c1.metric("Current price", format_price(last_price))
        c2.metric("Monthly change", format_percent(monthly_change))

        st.line_chart(data["Close"])

        if st.button("Add to watchlist"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)

# ==================================================
# RIGHT COLUMN
# ==================================================
with right_col:
    st.subheader("Watchlist")
    if st.session_state.watchlist:
        for w in st.session_state.watchlist:
            st.write(w)
    else:
        st.caption("No assets saved yet.")

# ==================================================
# NEWS & INTELLIGENCE (BOTTOM)
# ==================================================
st.divider()
st.header("News & Intelligence")

tabs = st.tabs([
    "News summary",
    "News filter",
    "News vs price",
    "Watchlist details",
    "Alerts"
])

# Récupération des news via cache
news = get_news(ticker)

# ==================================================
# TAB 1 - NEWS SUMMARY
# ==================================================
with tabs[0]:
    st.subheader("AI-like news summary (heuristic)")

    positive_words = ["beat", "growth", "strong", "profit", "upgrade"]
    negative_words = ["miss", "weak", "loss", "downgrade", "risk"]

    score = 0
    for n in news:
        title = n.get("title", "").lower()
        if any(w in title for w in positive_words):
            score += 1
        if any(w in title for w in negative_words):
            score -= 1

    if score > 0:
        sentiment = "Positive"
    elif score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    st.metric("Overall sentiment", sentiment)
    st.write("Based on keyword analysis of recent headlines.")

# ==================================================
# TAB 2 - NEWS FILTER
# ==================================================
with tabs[1]:
    st.subheader("Filtered news")

    category = st.selectbox(
        "Filter by type",
        ["All", "Earnings", "Rumors", "Macro"]
    )

    for n in news:
        title = n.get("title", "")
        title_l = title.lower()

        if category == "All":
            st.write("-", title)
        elif category == "Earnings" and "earn" in title_l:
            st.write("-", title)
        elif category == "Rumors" and "rumor" in title_l:
            st.write("-", title)
        elif category == "Macro" and "fed" in title_l:
            st.write("-", title)

# ==================================================
# TAB 3 - NEWS VS PRICE
# ==================================================
with tabs[2]:
    st.subheader("News impact vs price")
    if data is not None and not data.empty:
        recent = data.tail(60)
        st.line_chart(recent["Close"])
    st.caption("Visual comparison between recent news flow and price trend.")

# ==================================================
# TAB 4 - WATCHLIST DETAILS
# ==================================================
with tabs[3]:
    st.subheader("Your watchlist")

    if not st.session_state.watchlist:
        st.info("No assets in watchlist.")
    else:
        for w in st.session_state.watchlist:
            hist = get_history(w)
            if hist is not None and not hist.empty:
                change = (
                    hist["Close"].iloc[-1] - hist["Close"].iloc[0]
                ) / hist["Close"].iloc[0] * 100
                st.metric(w, format_percent(change))

# ==================================================
# TAB 5 - ALERTS
# ==================================================
with tabs[4]:
    st.subheader("Alerts")

    st.write(
        "Alerts are triggered when:\n"
        "- strong negative news keywords appear\n"
        "- or monthly price change exceeds +/-10%"
    )

    if data is not None and not data.empty and len(data) > 22:
        last_price = data["Close"].iloc[-1]
        prev_month = data["Close"].iloc[-22]
        monthly_change = (last_price - prev_month) / prev_month * 100
        if abs(monthly_change) > 10:
            st.warning("Price alert: strong monthly movement detected.")

# ==================================================
# FOOTER
# ==================================================
now_paris = datetime.now(ZoneInfo("Europe/Paris"))
st.divider()
st.caption("Last update: " + now_paris.strftime("%Y-%m-%d %H:%M:%S"))
