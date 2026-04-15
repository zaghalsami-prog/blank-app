import streamlit as st
import yfinance as yf
import requests
from datetime import datetime

# ===============================
# CONFIG
# ===============================
st.set_page_config(page_title="Market Intelligence", layout="wide")

st.title("Market Intelligence Dashboard")
st.write("Search assets and display related market news")

# ===============================
# SECTION RECHERCHE
# ===============================
st.divider()
st.header("Search Asset & Market News")

asset_type = st.selectbox(
    "Asset type",
    ["Stock", "Crypto"]
)

query = st.text_input(
    "Search asset",
    placeholder="Examples: AAPL, TSLA, BTC, ETH"
)

if query:
    query = query.upper()

# ===============================
# NEWS - ACTIONS (Yahoo Finance)
# ===============================
if asset_type == "Stock" and query:

    st.subheader(f"Latest news for {query}")

    try:
        stock = yf.Ticker(query)
        news = stock.news if stock.news else []

        if not news:
            st.info("No news found for this stock.")
        else:
            positive_words = ["beat", "growth", "strong", "upgrade", "profit"]
            negative_words = ["miss", "weak", "loss", "downgrade", "risk"]
            score = 0

            for item in news[:5]:
                title = item.get("title", "")
                publisher = item.get("publisher", "")
                link = item.get("link", "")
                ts = item.get("providerPublishTime")

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

            if score > 0:
                sentiment = "Positive"
            elif score < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            st.metric("News sentiment", sentiment)

    except Exception as e:
        st.error("Error loading stock news.")

# ===============================
# NEWS - CRYPTOS (CryptoPanic)
# ===============================
if asset_type == "Crypto" and query:

    st.subheader(f"Latest crypto news for {query}")

    if "CRYPTOPANIC_API_KEY" not in st.secrets:
        st.info("Crypto news disabled (no API key in Secrets).")
    else:
        try:
            url = "https://cryptopanic.com/api/v1/posts/"
            params = {
                "auth_token": st.secrets["CRYPTOPANIC_API_KEY"],
                "currencies": query,
                "kind": "news"
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            news = data.get("results", [])

            if not news:
                st.info("No crypto news found.")
            else:
                score = 0

                for item in news[:5]:
                    title = item.get("title", "")
                    link = item.get("url", "")

                    if item.get("positive"):
                        score += 1
                    if item.get("negative"):
                        score -= 1

                    st.markdown(f"- **{title}**  \n  {link}")

                if score > 0:
                    sentiment = "Positive"
                elif score < 0:
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"

                st.metric("News sentiment", sentiment)

        except Exception as e:
            st.error("Error loading crypto news.")
