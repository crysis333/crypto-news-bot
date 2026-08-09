import os
import json
import hashlib
import time
import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_news.json"
START_FILE = "bot_initialized.txt"

COINS = {
    "INJ": "Injective crypto",
    "DOGE": "Dogecoin crypto",
    "DOT": "Polkadot crypto",
    "ATOM": "Cosmos ATOM crypto",
    "CHR": "Chromia crypto",
    "SCRT": "Secret Network crypto",
    "OSMO": "Osmosis crypto",
    "SAGA": "Saga crypto blockchain",
    "DYM": "Dymension crypto",
    "CAKE": "PancakeSwap crypto",
    "SEI": "Sei Network crypto",
    "AVAX": "Avalanche crypto",
    "JUNO": "Juno crypto",
    "MINA": "Mina Protocol crypto",
    "NEAR": "NEAR Protocol crypto",
    "AKT": "Akash Network crypto",
    "OFC": "One Football Club crypto",
    "PORTAL": "Portal crypto token",
    "GMRX": "Gaimin GMRX crypto",
    "NOT": "Notcoin crypto",
    "DOGS": "DOGS crypto Telegram",
    "TIA": "Celestia crypto",
    "APT": "Aptos crypto",
    "AEVO": "Aevo crypto",
    "FIL": "Filecoin crypto",
    "EIGEN": "EigenLayer crypto",
    "GRT": "The Graph crypto",
    "JUP": "Jupiter crypto",
    "PYTH": "Pyth Network crypto",
    "WINK": "WINkLink crypto WIN",
    "BTC": "Bitcoin BTC crypto",
    "ETH": "Ethereum ETH crypto",
}

REDDIT_SUBREDDITS = [
    "CryptoCurrency",
    "CryptoMarkets",
    "Bitcoin",
    "ethereum",
    "dogecoin",
    "Polkadot",
    "CosmosNetwork",
    "Avalanche",
    "nearprotocol",
    "MinaProtocol",
    "Celestia",
    "Aptos",
    "Filecoin",
]

BLOCKED_SOURCES = [
    "bybit.com",
    "binance.com",
    "coinmarketcap.com",
    "coingecko.com",
    "kraken.com",
    "okx.com",
    "kucoin.com",
]

BLOCKED_WORDS = [
    "calculator",
    "converter",
    "convert",
    "conversion",
    "to usd",
    "to eur",
    "exchange rate",
    "price converter",
    "currency converter",
    "how much is",
    "price today",
    "price now",
]

NEWS_KEYWORDS = [
    "hack", "hacked", "exploit", "exploited",
    "attack", "security", "vulnerability",
    "partnership", "partner", "integration",
    "collaboration", "launch", "launched",
    "mainnet", "testnet", "upgrade", "update",
    "release", "listing", "listed", "delisting",
    "delisted", "etf", "regulation", "regulatory",
    "sec", "lawsuit", "legal", "ban", "banned",
    "funding", "investment", "investor",
    "acquisition", "staking", "validator",
    "governance", "airdrop", "adoption",
    "institutional", "developer", "developers",
    "development", "proposal", "vote", "voting",
    "milestone", "record", "surge", "rally",
    "collapse", "crash", "tokenomics",
    "burn", "mint", "unlock", "network",
]

POSITIVE_WORDS = [
    "approve", "approved", "approval",
    "bullish", "surge", "rally",
    "partnership", "launch", "launched",
    "upgrade", "growth", "adoption",
    "record", "increase", "gain", "gains",
    "positive", "breakout", "integrated",
    "integration", "listing", "support",
    "success", "milestone", "funding",
    "investment", "expands", "expansion",
]

NEGATIVE_WORDS = [
    "hack", "hacked", "exploit",
    "exploited", "scam", "fraud",
    "lawsuit", "ban", "banned",
    "collapse", "crash", "drop",
    "drops", "decline", "declines",
    "loss", "losses", "negative",
    "attack", "stolen", "delist",
    "delisted", "warning",
    "investigation", "investigated",
]

IMPORTANT_WORDS = {
    "hack": 5,
    "hacked": 5,
    "exploit": 5,
    "exploited": 5,
    "attack": 5,
    "stolen": 5,
    "etf": 5,
    "approval": 4,
    "approved": 4,
    "lawsuit": 4,
    "ban": 5,
    "banned": 5,
    "delisting": 5,
    "delisted": 5,
    "mainnet": 4,
    "security": 4,
    "shutdown": 5,
    "collapse": 5,
    "partnership": 3,
    "upgrade": 3,
    "launch": 3,
    "listing": 3,
    "funding": 3,
    "investment": 3,
    "acquisition": 4,
    "record": 3,
    "governance": 2,
    "staking": 2,
    "airdrop": 2,
    "unlock": 3,
}


# ---------------------------------------
# Crypto terminology
# ---------------------------------------

CRYPTO_TERMS = {
    "burn-and-mint equilibrium":
        "تعادل سوزاندن و ایجاد توکن",

    "burn and mint equilibrium":
        "تعادل سوزاندن و ایجاد توکن",

    "burning mechanism":
        "سازوکار سوزاندن توکن",

    "token burn":
        "سوزاندن توکن",

    "token burning":
        "سوزاندن توکن",

    "minting":
        "ایجاد توکن",

    "mint":
        "ایجاد توکن",

    "staking":
        "استیکینگ",

    "staked":
        "استیک‌شده",

    "validator":
        "اعتبارسنج",

    "validators":
        "اعتبارسنج‌ها",

    "mainnet":
        "مین‌نت",

    "testnet":
        "تست‌نت",

    "governance":
        "حاکمیت شبکه",

    "airdrop":
        "ایردراپ",

    "token unlock":
        "آزادسازی توکن",

    "token unlocks":
        "آزادسازی توکن‌ها",

    "unlock":
        "آزادسازی توکن",

    "liquidity":
        "نقدینگی",

    "liquidity pool":
        "استخر نقدینگی",

    "total value locked":
        "ارزش کل دارایی‌های قفل‌شده",

    "tokenomics":
        "توکنومیک",

    "market cap":
        "ارزش بازار",

    "market capitalization":
        "ارزش بازار",

    "on-chain":
        "آن‌چین",

    "onchain":
        "آن‌چین",

    "layer 1":
        "لایه اول",

    "layer-1":
        "لایه اول",

    "layer 2":
        "لایه دوم",

    "layer-2":
        "لایه دوم",

    "rollup":
        "رول‌آپ",

    "bridge":
        "بریج",

    "cross-chain":
        "کراس‌چین",

    "smart contract":
        "قرارداد هوشمند",

    "decentralized finance":
        "امور مالی غیرمتمرکز",

    "defi":
        "دیفای",

    "decentralized exchange":
        "صرافی غیرمتمرکز",

    "dex":
        "صرافی غیرمتمرکز",

    "centralized exchange":
        "صرافی متمرکز",

    "cex":
        "صرافی متمرکز",

    "whale":
        "نهنگ",

    "whales":
        "نهنگ‌ها",

    "institutional investors":
        "سرمایه‌گذاران نهادی",

    "institutional":
        "نهادی",

    "funding":
        "تأمین مالی",

    "venture capital":
        "سرمایه‌گذاری خطرپذیر",

    "protocol":
        "پروتکل",

    "network upgrade":
        "ارتقای شبکه",

    "network upgrade":
        "ارتقای شبکه",

    "partnership":
        "همکاری",

    "partnerships":
        "هم
