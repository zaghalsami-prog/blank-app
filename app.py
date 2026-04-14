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
st.caption("Cryptos & actions – multi‑marchés")

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
crypto_dict = {c["name"]: c["id"] for c in cryptos}

crypto_name = st.selectbox(
    "Choisis une crypto",
    options=sorted(crypto_dict.keys()),
    index=sorted(crypto_dict.keys()).index("Bitcoin")
)

crypto_id = crypto_dict[crypto_name]
crypto_data = get_crypto_price(crypto_id)

if crypto_id in crypto_data:
    data = crypto_data[crypto_id]
    st.metric(
        label=crypto_name,
        value=f"${data['usd']:,}",
        delta=f"{data['usd_24h_change']:.2f}%"
    )

# ==================================================
# ACTIONS – MARCHÉS
# ==================================================
st.subheader("📈 Actions & Indices")

CAC40 = {
    "Accor": "AC.PA", "Air Liquide": "AI.PA", "Airbus": "AIR.PA",
    "Alstom": "ALO.PA", "ArcelorMittal": "MT.AS", "AXA": "CS.PA",
    "BNP Paribas": "BNP.PA", "Bouygues": "EN.PA", "Capgemini": "CAP.PA",
    "Carrefour": "CA.PA", "Crédit Agricole": "ACA.PA",
    "Danone": "BN.PA", "Dassault Systèmes": "DSY.PA",
    "Edenred": "EDEN.PA", "Engie": "ENGI.PA",
    "EssilorLuxottica": "EL.PA", "Hermès": "RMS.PA",
    "Kering": "KER.PA", "Legrand": "LR.PA",
    "L'Oréal": "OR.PA", "LVMH": "MC.PA",
    "Michelin": "ML.PA", "Orange": "ORA.PA",
    "Pernod Ricard": "RI.PA", "Publicis": "PUB.PA",
    "Renault": "RNO.PA", "Safran": "SAF.PA",
    "Saint-Gobain": "SGO.PA", "Sanofi": "SAN.PA",
    "Schneider Electric": "SU.PA", "Société Générale": "GLE.PA",
    "Stellantis": "STLAM.MI", "STMicroelectronics": "STM.PA",
    "Teleperformance": "TEP.PA", "Thales": "HO.PA",
    "TotalEnergies": "TTE.PA", "Unibail-Rodamco": "URW.AS",
    "Veolia": "VIE.PA", "Vinci": "DG.PA"
}

US_STOCKS = {
    "Apple": "AAPL", "Microsoft": "MSFT",
    "Nvidia": "NVDA", "Tesla": "TSLA",
    "Amazon": "AMZN", "Meta": "META"
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
    st.error("Erreur de chargement des données.")

# ==================================================
# FOOTER – HEURE FRANCE
# ==================================================
st.divider()
paris_time = datetime.now(ZoneInfo("Europe/Paris"))
st.caption("Mise à jour : " + paris_time.strftime("%d/%m/%Y %H:%M:%S"))
