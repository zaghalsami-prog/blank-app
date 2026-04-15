import streamlit as st
import yfinance as yf
import requests
from datetime import datetime

st.divider()
st.header("🔍 Search & Market News")

# ---------------------------------------
# 1. Asset type selection
# ---------------------------------------
asset_type = st.selectbox(
    "Asset type",
    ["Stock", "Crypto"]
)

query = st.text_input(
    "Search an asset",
    placeholder="Examples: AAPL, TSLA, ASML.AS, BTC, ETH"
).upper()

# ---------------------------------------
# 2. STOCK NEWS - Yahoo Finance
# ---------------------------------------
if asset_type == "Stock" and query:
    st.subheader(f"📰 Latest news for {query}")

    try:
        stock = yf.Ticker(query)
        news = stock.news

        if not news:
            st.info("No recent news found.")
        else:
            positive_words = ["beat", "growth", "strong", "upgrade", "profit"]
            negative_words = ["miss", "weak", "loss", "downgrade", "risk"]

            score = 0

            for n in news[:5]:
                title = n.get("title", "")
                publisher = n.get("publisher", "")
                link = n.get("link", "")
                ts = n.get("providerPublishTime")

                if any(w in title.lower() for w in positive_words):
                    score += 1
                if any(w in title.lower() for w in negative_words):
                    score -= 1

                date = (
                    datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    if ts else ""
                )

                st.markdown(
                    f"- **{title}**  \n"
                    f"  Source: {publisher} | {date}  \n"
                    f"  {link}"
                )

            sentiment = (
                "Positive" if score > 0
                else "Negative" if score < 0
                else "Neutral"
            )

            st.metric("News sentiment", sentiment)

    except Exception:
        st.warning("Unable to load stock news.")

# ---------------------------------------
# 3. CRYPTO NEWS - CryptoPanic
# ---------------------------------------
if asset_type == "Crypto" and query:
    st.subheader(f"📰 Latest crypto news for {query}")

    try:
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            "auth_token": st.secrets["CRYPTOPANIC_API_KEY"],
            "currencies": query,
            "kind": "news"
        }

        r = requests.get(url, params=params, timeout=10)
        news = r.json().get("results", [])

        if not news:
            st.info("No recent crypto news found.")
        else:
            score = 0

            for n in news[:5]:
                title = n.get("title", "")
                link = n.get("url", "")

                if n.get("positive"):
                    score += 1
                if n.get("negative"):
                    score -= 1

                st.markdown(f"- **{title}**  \n  {link}")

            sentiment = (
                "Positive" if score > 0
                else "Negative" if score < 0
                else "Neutral"
            )

            st.metric("News sentiment", sentiment)

    except Exception:
        st.warning("Unable to load crypto news.")
``
