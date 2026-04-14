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
st.caption("TOP 100 cryptos & actions – multi‑marchés")

# ==================================================
# CRYPTOS – TOP 100 COINGECKO
# ==================================================
@st.cache_data(ttl=300)
def get_top_100_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "24h"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

st.subheader("🪙 Cryptomonnaies (TOP 100)")

cryptos = get_top_100_cryptos()

crypto_dict = {
    f"{c['market_cap_rank']}. {c['name']} ({c['symbol'].upper()})": c
    for c in cryptos
}

selected_crypto_label = st.selectbox(
    "Choisis une crypto (TOP 100)",
    options=list(crypto_dict.keys()),
    index=0
)

selected_crypto = crypto_dict[selected_crypto_label]

st.metric(
    label=selected_crypto["name"],
    value=f"${selected_crypto['current_price']:,}",
    delta=f"{selected_crypto['price_change_percentage_24h']:.2f}%"
)

# ==================================================
# ACTIONS – MARCHÉS
# ==================================================
st.subheader("📈 Actions & Indices")

CAC40 = {
    "Accor": "AC.PA", "Air Liquide": "AI.PA", "Airbus": "AIR.PA",
    "Alstom": "ALO.PA", "ArcelorMittal": "MT.AS", "AXA": "CS.PA",
    "BNP Paribas": "BNP.PA", "Bouygues": "EN.PA", "Capgemini": "CAP.PA",
    "Carrefour": "CA.PA", "Crédit Agricole": "ACA.PA", "Danone": "BN.PA",
    "Dassault Systèmes": "DSY.PA", "Edenred": "EDEN.PA", "Engie": "ENGI.PA",
    "EssilorLuxottica": "EL.PA", "Hermès": "RMS.PA", "Kering": "KER.PA",
    "Legrand": "LR.PA", "L'Oréal": "OR.PA", "LVMH": "MC.PA",
    "Michelin": "ML.PA", "Orange": "ORA.PA", "Pernod Ricard": "RI.PA",
    "Publicis": "PUB.PA", "Renault": "RNO.PA", "Safran": "SAF.PA",
    "Saint-Gobain": "SGO.PA", "Sanofi": "SAN.PA",
    "Schneider Electric": "SU.PA", "Société Générale": "GLE.PA",
    "Stellantis": "STLAM.MI", "STMicroelectronics": "STM.PA",
    "Teleperformance": "TEP.PA", "Thales": "HO.PA",
    "TotalEnergies": "TTE.PA", "Unibail-Rodamco": "URW.AS",
    "Veolia": "VIE.PA", "Vinci": "DG.PA"
}

US_STOCKS = {
    "Apple": "AAPL", "Microsoft": "MSFT", "Nvidia": "NVDA",
    "Tesla": "TSLA", "Amazon": "AMZN", "Meta": "META"
}

INDICES = {
    "S&P 500": "^GSPC", "Nasdaq": "^IXIC",
    "CAC 40": "^FCHI", "DAX": "^GDAXI"
}

MARKETS = {
    "🇫🇷 CAC 40": CAC40,
    "🇺🇸 Actions US": US_STOCKS,
    "📊 Indices": INDICES
}

market = st.selectbox("Choisis un marché", list(MARKETS.keys()))
asset_name = st.selectbox("Choisis un actif", list(MARKETS[market].keys()))
ticker = MARKETS[market][asset_name]

try:
    hist = yf.Ticker(ticker).history(period="5d")

    if len(hist) >= 2:
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        delta = (price - prev) / prev * 100

        st.metric(
            label=f"{asset_name} ({ticker})",
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
