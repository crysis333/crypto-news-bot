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


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_news.json"
START_FILE = "bot_initialized.txt"


# ============================================================
# COINS
# ============================================================

COINS = {
    "INJ": "Injective",
    "DOGE": "Dogecoin",
    "DOT": "Polkadot",
    "ATOM": "Cosmos",
    "CHR": "Chromia",
    "SCRT": "Secret Network",
    "OSMO": "Osmosis",
    "SAGA": "Saga",
    "DYM": "Dymension",
    "CAKE": "PancakeSwap",
    "SEI": "Sei Network",
    "AVAX": "Avalanche",
    "JUNO": "Juno",
    "MINA": "Mina Protocol",
    "NEAR": "NEAR Protocol",
    "AKT": "Akash Network",
    "OFC": "OFC",
    "PORTAL": "Portal",
    "GMRX": "Gaimin",
    "NOT": "Notcoin",
    "DOGS": "DOGS",
    "TIA": "Celestia",
    "APT": "Aptos",
    "AEVO": "Aevo",
    "FIL": "Filecoin",
    "EIGEN": "EigenLayer",
    "GRT": "The Graph",
    "JUP": "Jupiter",
    "PYTH": "Pyth Network",
    "WINK": "WINkLink",
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
}


# ============================================================
# REDDIT
# ============================================================

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


# ============================================================
# FILTERS
# ============================================================

BLOCKED_SOURCES = [
    "bybit.com",
    "binance.com",
    "kraken.com",
    "okx.com",
    "kucoin.com",
]


BLOCKED_WORDS = [
    "calculator",
    "converter",
    "convert",
    "conversion",
    "exchange rate",
    "price converter",
    "currency converter",
    "how much is",
    "to usd",
    "to eur",
    "usd to",
    "eur to",
]


NEWS_KEYWORDS = [
    "hack",
    "hacked",
    "exploit",
    "exploited",
    "attack",
    "security",
    "vulnerability",
    "partnership",
    "partner",
    "integration",
    "collaboration",
    "launch",
    "launched",
    "mainnet",
    "testnet",
    "upgrade",
    "update",
    "release",
    "listing",
    "listed",
    "delisting",
    "delisted",
    "etf",
    "regulation",
    "regulatory",
    "sec",
    "lawsuit",
    "legal",
    "ban",
    "banned",
    "funding",
    "investment",
    "investor",
    "acquisition",
    "staking",
    "validator",
    "governance",
    "airdrop",
    "adoption",
    "institutional",
    "developer",
    "developers",
    "development",
    "proposal",
    "vote",
    "voting",
    "milestone",
    "record",
    "surge",
    "rally",
    "collapse",
    "crash",
    "burn",
    "mint",
    "unlock",
    "breakout",
    "breakthrough",
    "accumulate",
    "accumulation",
    "whale",
    "whales",
    "sell",
    "selling",
    "buy",
    "buying",
    "price",
    "volume",
    "flows",
    "inflows",
    "outflows",
]


POSITIVE_WORDS = [
    "approve",
    "approved",
    "approval",
    "bullish",
    "surge",
    "rally",
    "partnership",
    "launch",
    "launched",
    "upgrade",
    "growth",
    "adoption",
    "record",
    "increase",
    "gain",
    "gains",
    "positive",
    "breakout",
    "breakthrough",
    "integrated",
    "integration",
    "listing",
    "support",
    "success",
    "milestone",
    "funding",
    "investment",
    "expands",
    "expansion",
]


NEGATIVE_WORDS = [
    "hack",
    "hacked",
    "exploit",
    "exploited",
    "scam",
    "fraud",
    "lawsuit",
    "ban",
    "banned",
    "collapse",
    "crash",
    "drop",
    "drops",
    "decline",
    "declines",
    "loss",
    "losses",
    "negative",
    "attack",
    "stolen",
    "delist",
    "delisted",
    "warning",
    "investigation",
    "investigated",
    "sell",
    "selling",
]


IMPORTANT_WORDS = {
    "hack": 6,
    "hacked": 6,
    "exploit": 6,
    "exploited": 6,
    "attack": 5,
    "stolen": 6,
    "etf": 5,
    "approval": 5,
    "approved": 5,
    "lawsuit": 4,
    "ban": 5,
    "banned": 5,
    "delisting": 5,
    "delisted": 5,
    "mainnet": 4,
    "security": 4,
    "shutdown": 6,
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
    "breakout": 2,
    "breakthrough": 3,
    "whale": 2,
    "whales": 2,
    "accumulate": 3,
    "accumulation": 3,
}


# ============================================================
# PROJECT NAMES
# ============================================================

PROJECT_NAMES = {
    "INJ": "اینجکتیو",
    "DOGE": "دوج‌کوین",
    "DOT": "پولکادات",
    "ATOM": "کازماس",
    "CHR": "کرومیا",
    "SCRT": "سیکرت نتورک",
    "OSMO": "اُسموسیس",
    "SAGA": "ساگا",
    "DYM": "دایمنشن",
    "CAKE": "پنکیک‌سواپ",
    "SEI": "Sei",
    "AVAX": "آوالانچ",
    "JUNO": "جونو",
    "MINA": "مینا",
    "NEAR": "نیر",
    "AKT": "آکاش",
    "OFC": "OFC",
    "PORTAL": "پورتال",
    "GMRX": "گیمین",
    "NOT": "نات‌کوین",
    "DOGS": "DOGS",
    "TIA": "سلسستیا",
    "APT": "آپتوس",
    "AEVO": "Aevo",
    "FIL": "فایل‌کوین",
    "EIGEN": "EigenLayer",
    "GRT": "The Graph",
    "JUP": "Jupiter",
    "PYTH": "Pyth",
    "WINK": "WINkLink",
    "BTC": "بیت‌کوین",
    "ETH": "اتریوم",
}


# ============================================================
# HTTP
# ============================================================

def fetch_url(url, timeout=20):

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "(compatible; CryptoNewsBot/7.0)"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            return response.read()

    except Exception as error:

        print(
            "Fetch error:",
            url,
            error
        )

        return None


# ============================================================
# STORAGE
# ============================================================

def load_seen():

    if not os.path.exists(SEEN_FILE):
        return set()

    try:

        with open(
            SEEN_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return set(
                json.load(file)
            )

    except Exception as error:

        print(
            "Seen file error:",
            error
        )

        return set()


def save_seen(seen):

    try:

        data = list(seen)[-5000:]

        with open(
            SEEN_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False
            )

    except Exception as error:

        print(
            "Save seen error:",
            error
        )


def make_id(text):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================
# TEXT
# ============================================================

def normalize_text(text):

    text = html.unescape(
        text or ""
    )

    text = text.lower()

    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def similarity(a, b):

    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b)
    ).ratio()


# ============================================================
# ARTICLE FILTER
# ============================================================

def is_blocked_article(article):

    title = article.get(
        "title",
        ""
    ).lower()

    source = article.get(
        "source",
        ""
    ).lower()

    text = title + " " + source

    for source_name in BLOCKED_SOURCES:

        if source_name in source:
            return True

    for word in BLOCKED_WORDS:

        if word in text:
            return True

    return False


def is_news_article(article):

    if is_blocked_article(article):
        return False

    title = article.get(
        "title",
        ""
    ).lower()

    return any(
        keyword in title
        for keyword in NEWS_KEYWORDS
    )


# ============================================================
# GOOGLE NEWS
# ============================================================

def get_google_news(query):

    encoded = urllib.parse.quote(
        query
    )

    url = (
        "https://news.google.com/rss/search?"
        "q="
        + encoded
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    data = fetch_url(url)

    if not data:
        return []

    try:

        root = ET.fromstring(
            data
        )

        articles = []

        for item in root.findall(
            "./channel/item"
        )[:30]:

            title = item.findtext(
                "title",
                ""
            )

            link = item.findtext(
                "link",
                ""
            )

            date = item.findtext(
                "pubDate",
                ""
            )

            source_element = item.find(
                "source"
            )

            source = ""

            if source_element is not None:

                source = (
                    source_element.text
                    or ""
                )

            article = {
                "title": title.strip(),
                "link": link.strip(),
                "date": date.strip(),
                "source": source.strip(),
                "type": "news",
            }

            if is_news_article(
                article
            ):

                articles.append(
                    article
                )

        return articles

    except Exception as error:

        print(
            "Google News error:",
            error
        )

        return []


# ============================================================
# REDDIT
# ============================================================

def get_reddit(subreddit):

    url = (
        "https://www.reddit.com/r/"
        + subreddit
        + "/new/.rss"
    )

    data = fetch_url(url)

    if not data:
        return []

    try:

        root = ET.fromstring(
            data
        )

        namespace = {
            "atom":
                "http://www.w3.org/2005/Atom"
        }

        articles = []

        for entry in root.findall(
            "atom:entry",
            namespace
        )[:20]:

            title = entry.findtext(
                "atom:title",
                "",
                namespace
            )

            updated = entry.findtext(
                "atom:updated",
                "",
                namespace
            )

            link_element = entry.find(
                "atom:link",
                namespace
            )

            link = ""

            if link_element is not None:

                link = link_element.attrib.get(
                    "href",
                    ""
                )

            articles.append({
                "title": title.strip(),
                "link": link.strip(),
                "date": updated.strip(),
                "source":
                    "Reddit / r/"
                    + subreddit,
                "type": "reddit",
            })

        return articles

    except Exception as error:

        print(
            "Reddit error:",
            error
        )

        return []


# ============================================================
# COIN MATCHING
# ============================================================

def article_matches_coin(
    symbol,
    project,
    article
):

    if is_blocked_article(
        article
    ):
        return False

    title = normalize_text(
        article.get(
            "title",
            ""
        )
    )

    project_lower = project.lower()

    if symbol in [
        "BTC",
        "ETH",
    ]:

        if symbol == "BTC":

            return (
                "bitcoin" in title
                or re.search(
                    r"\bbtc\b",
                    title
                ) is not None
            )

        return (
            "ethereum" in title
            or re.search(
                r"\beth\b",
                title
            ) is not None
        )

    if re.search(
        r"\b"
        + re.escape(
            symbol.lower()
        )
        + r"\b",
        title
    ):

        return True

    project_words = project_lower.split()

    for word in project_words:

        if len(word) >= 4:

            if word in title:
                return True

    return False


# ============================================================
# NEWS REWRITE ENGINE
# ============================================================

def clean_title(title):

    title = html.unescape(
        title or ""
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    title = title.strip()

    title = re.sub(
        r"\s+[|•]\s+.*$",
        "",
        title
    )

    return title


def percent_value(text):

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        text
    )

    if match:

        return match.group(1) + "%"

    return None


def extract_project_name(
    symbol,
    title
):

    project = PROJECT_NAMES.get(
        symbol,
        symbol
    )

    return (
        project
        + " ("
        + symbol
        + ")"
    )


def rewrite_crypto_title(
    symbol,
    original
):

    title = clean_title(
        original
    )

    lower = title.lower()

    project = extract_project_name(
        symbol,
        title
    )

    percent = percent_value(
        title
    )

    # --------------------------------------------------------
    # TOKEN UNLOCK + WHALES + PRICE
    # --------------------------------------------------------

    if (
        ("whale" in lower or "whales" in lower)
        and (
            "unlock" in lower
            or "unlocked" in lower
        )
        and (
            "accumulate" in lower
            or "accumulation" in lower
        )
    ):

        if (
            "price lag" in lower
            or "price lags" in lower
            or "price remains weak" in lower
        ):

            return (
                "نهنگ‌ها پس از آزادسازی توکن، "
                "در حال انباشت "
                + symbol
                + " هستند؛ "
                "قیمت همچنان تحت فشار است"
            )

        return (
            "نهنگ‌ها پس از آزادسازی توکن، "
            "در حال انباشت "
            + symbol
            + " هستند"
        )

    # --------------------------------------------------------
    # WHALE ACCUMULATION
    # --------------------------------------------------------

    if (
        ("whale" in lower or "whales" in lower)
        and (
            "accumulate" in lower
            or "accumulation" in lower
        )
    ):

        return (
            "نهنگ‌ها در حال انباشت "
            + symbol
            + " هستند"
        )

    # --------------------------------------------------------
    # WHALE SELLING
    # --------------------------------------------------------

    if (
        ("whale" in lower or "whales" in lower)
        and (
            "sell" in lower
            or "selling" in lower
            or "sold" in lower
        )
    ):

        return (
            "نهنگ‌ها در حال فروش "
            + symbol
            + " هستند"
        )

    # --------------------------------------------------------
    # SURGE / RALLY
    # --------------------------------------------------------

    if (
        "surge" in lower
        or "surges" in lower
    ):

        if percent:

            return (
                project
                + " با رشد "
                + percent
                + " جهش کرد"
            )

        return (
            project
            + " با جهش قیمت مواجه شد"
        )

    if (
        "rally" in lower
        or "rallies" in lower
    ):

        if percent:

            return (
                project
                + " با رشد "
                + percent
                + " وارد یک رالی صعودی شد"
            )

        return (
            project
            + " وارد یک رالی صعودی شد"
        )

    # --------------------------------------------------------
    # BREAKOUT
    # --------------------------------------------------------

    if (
        "breakout" in lower
        or "breaks resistance" in lower
        or "breaks key resistance" in lower
    ):

        if percent:

            return (
                project
                + " "
                + percent
                + " رشد کرد و مقاومت مهمی را شکست"
            )

        return (
            project
            + " مقاومت مهمی را شکست"
        )

    # --------------------------------------------------------
    # PRICE DROP
    # --------------------------------------------------------

    if (
        "drops" in lower
        or "drop" in lower
        or "falls" in lower
        or "fall" in lower
        or "declines" in lower
        or "decline" in lower
        or "plunges" in lower
        or "plunge" in lower
    ):

        if percent:

            return (
                project
                + " با افت "
                + percent
                + " مواجه شد"
            )

        return (
            project
            + " با کاهش قیمت مواجه شد"
        )

    # --------------------------------------------------------
    # PRICE INCREASE
    # --------------------------------------------------------

    if (
        "rises" in lower
        or "rise" in lower
        or "gains" in lower
        or "gain" in lower
        or "increases" in lower
        or "increase" in lower
    ):

        if percent:

            return (
                project
                + " "
                + percent
                + " رشد کرد"
            )

        return (
            project
            + " رشد کرد"
        )

    # --------------------------------------------------------
    # TOKEN UNLOCK
    # --------------------------------------------------------

    if (
        "token unlock" in lower
        or "tokens unlocked" in lower
        or "unlocking tokens" in lower
    ):

        return (
            "آزادسازی توکن‌های "
            + symbol
            + " در راه است"
        )

    # --------------------------------------------------------
    # PARTNERSHIP
    # --------------------------------------------------------

    if (
        "partnership" in lower
        or "partners with" in lower
        or "partnership with" in lower
    ):

        return (
            project
            + " با یک همکاری جدید خبرساز شد"
        )

    # --------------------------------------------------------
    # MAINNET
    # --------------------------------------------------------

    if "mainnet" in lower:

        if "launch" in lower or "launched" in lower:

            return (
                "مین‌نت "
                + project
                + " راه‌اندازی شد"
            )

        if "upgrade" in lower:

            return (
                "ارتقای مهمی برای مین‌نت "
                + project
                + " منتشر شد"
            )

        return (
            "تحولات جدیدی در مین‌نت "
            + project
            + " رخ داده است"
        )

    # --------------------------------------------------------
    # UPGRADE
    # --------------------------------------------------------

    if (
        "upgrade" in lower
        or "upgraded" in lower
    ):

        return (
            project
            + " یک ارتقای مهم را دریافت کرد"
        )

    # --------------------------------------------------------
    # HACK / EXPLOIT
    # --------------------------------------------------------

    if (
        "hack" in lower
        or "hacked" in lower
        or "exploit" in lower
        or "exploited" in lower
    ):

        return (
            "هشدار امنیتی برای "
            + project
            + ": گزارش هک یا سوءاستفاده منتشر شد"
        )

    # --------------------------------------------------------
    # LISTING
    # --------------------------------------------------------

    if (
        "listed" in lower
        or "listing" in lower
    ):

        return (
            project
            + " در یک صرافی یا بازار جدید لیست شد"
        )

    # --------------------------------------------------------
    # ETF
    # --------------------------------------------------------

    if "etf" in lower:

        return (
            "تحولات جدید مربوط به ETF "
            + project
        )

    # --------------------------------------------------------
    # FUNDING
    # --------------------------------------------------------

    if (
        "funding" in lower
        or "investment" in lower
    ):

        return (
            project
            + " سرمایه‌گذاری یا تأمین مالی جدید جذب کرد"
        )

    # --------------------------------------------------------
    # ADOPTION
    # --------------------------------------------------------

    if "adoption" in lower:

        return (
            "پذیرش "
            + project
            + " افزایش یافته است"
        )

    # --------------------------------------------------------
    # STAKING
    # --------------------------------------------------------

    if "staking" in lower:

        return (
            "تحولات جدیدی در استیکینگ "
            + project
            + " گزارش شد"
        )

    # --------------------------------------------------------
    # GOVERNANCE
    # --------------------------------------------------------

    if (
        "governance" in lower
        or "proposal" in lower
        or "vote" in lower
    ):

        return (
            "پیشنهاد یا رأی‌گیری جدید در اکوسیستم "
            + project
        )

    # --------------------------------------------------------
    # RECORD
    # --------------------------------------------------------

    if "record" in lower:

        return (
            project
            + " به یک رکورد جدید رسید"
        )

    # --------------------------------------------------------
    # GENERIC CLEANUP
    # --------------------------------------------------------

    replacements = {
        "price": "قیمت",
        "crypto": "کریپتو",
        "token": "توکن",
        "network": "شبکه",
        "market": "بازار",
        "volume": "حجم معاملات",
        "users": "کاربران",
        "user": "کاربر",
        "developers": "توسعه‌دهندگان",
        "developer": "توسعه‌دهنده",
        "ecosystem": "اکوسیستم",
        "launch": "راه‌اندازی",
        "launched": "راه‌اندازی شد",
        "update": "به‌روزرسانی",
        "security": "امنیت",
    }

    result = title

    for old, new in replacements.items():

        result = re.sub(
            r"\b"
            + re.escape(old)
            + r"\b",
            new,
            result,
            flags=re.IGNORECASE
        )

    # اگر هنوز کاملاً انگلیسی بود،
    # ترجمه ماشینی خراب را ارسال نمی‌کنیم.
    if re.search(
        r"[A-Za-z]{4,}",
        result
    ):

        return (
            project
            + "؛ "
            + title
        )

    result = re.sub(
        r"\s+",
        " ",
        result
    )

    return result.strip()


# ============================================================
# SENTIMENT
# ============================================================

def analyze_sentiment(title):

    text = normalize_text(
        title
    )

    positive = 0
    negative = 0

    for word in POSITIVE_WORDS:

        if word in text:
            positive += 1

    for word in NEGATIVE_WORDS:

        if word in text:
            negative += 1

    if negative > positive:
        return "🔴 منفی"

    if positive > negative:
        return "🟢 مثبت"

    return "🟡 خنثی"


# ============================================================
# IMPORTANCE
# ============================================================

def importance_score(
    title,
    source,
    news_type
):

    text = normalize_text(
        title
        + " "
        + source
    )

    score = 3

    for word, value in IMPORTANT_WORDS.items():

        if word in text:
            score += value

    if (
        "hack" in text
        or "exploit" in text
        or "etf" in text
        or "approval" in text
    ):

        score += 1

    if news_type == "reddit":

        score -= 1

    return max(
        1,
        min(score, 10)
    )


def importance_label(score):

    if score >= 9:
        return "🚨 بسیار مهم"

    if score >= 7:
        return "🔥 مهم"

    if score >= 4:
        return "🟡 قابل توجه"

    return "⚪ کم‌اهمیت"


# ============================================================
# DUPLICATE FILTER
# ============================================================

def is_duplicate(
    article,
    previous
):

    title = article.get(
        "title",
        ""
    )

    link = article.get(
        "link",
        ""
    )

    for old in previous:

        old_link = old.get(
            "link",
            ""
        )

        old_title = old.get(
            "title",
            ""
        )

        if link and link == old_link:

            return True

        if similarity(
            title,
            old_title
        ) >= 0.88:

            return True

    return False


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):

    url = (
        "https://api.telegram.org/"
        "bot"
        + BOT_TOKEN
        + "/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False,
    }).encode(
        "utf-8"
    )

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            return response.read().decode(
                "utf-8"
            )

    except Exception as error:

        print(
            "Telegram error:",
            error
        )

        return None


# ============================================================
# MESSAGE
# ============================================================

def build_message(
    symbol,
    article
):

    original = clean_title(
        article.get(
            "title",
            ""
        )
    )

    persian = rewrite_crypto_title(
        symbol,
        original
    )

    source = article.get(
        "source",
        "Unknown"
    )

    score = importance_score(
        original,
        source,
        article.get(
            "type",
            "news"
        )
    )

    sentiment = analyze_sentiment(
        original
    )

    return (
        "📰 "
        + symbol
        + " | "
        + importance_label(score)
        + "\n\n"
        "🔹 "
        + persian
        + "\n\n"
        "📊 اهمیت: "
        + str(score)
        + "/10\n"
        "📈 تأثیر احتمالی: "
        + sentiment
        + "\n\n"
        "🇬🇧 Original:\n"
        + original
        + "\n\n"
        "🗞 منبع: "
        + source
        + "\n"
        "🔗 "
        + article.get(
            "link",
            ""
        )
    )


# ============================================================
# COLLECT
# ============================================================

def collect_news():

    all_articles = []

    for symbol, project in COINS.items():

        print(
            "Google News -> "
            + symbol
        )

        articles = get_google_news(
            project
            + " crypto"
        )

        for article in articles:

            if article_matches_coin(
                symbol,
                project,
                article
            ):

                item = dict(
                    article
                )

                item["symbol"] = symbol

                all_articles.append(
                    item
                )

    for subreddit in REDDIT_SUBREDDITS:

        print(
            "Reddit -> r/"
            + subreddit
        )

        articles = get_reddit(
            subreddit
        )

        for article in articles:

            if is_blocked_article(
                article
            ):

                continue

            for symbol, project in COINS.items():

                if article_matches_coin(
                    symbol,
                    project,
                    article
                ):

                    item = dict(
                        article
                    )

                    item["symbol"] = symbol

                    all_articles.append(
                        item
                    )

                    break

    return all_articles


# ============================================================
# FIRST RUN
# ============================================================

def initialize_bot():

    print(
        "First run detected."
    )

    print(
        "Old news will be ignored."
    )

    articles = collect_news()

    seen = load_seen()

    for article in articles:

        unique = (
            article.get(
                "symbol",
                ""
            )
            + "|"
            + article.get(
                "title",
                ""
            )
            + "|"
            + article.get(
                "link",
                ""
            )
        )

        seen.add(
            make_id(unique)
        )

    save_seen(seen)

    with open(
        START_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "initialized"
        )

    print(
        "Initialization complete."
    )

    print(
        "Registered "
        + str(len(articles))
        + " old articles."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    seen = load_seen()

    if not os.path.exists(
        START_FILE
    ):

        initialize_bot()

        return

    print(
        "Collecting new crypto news..."
    )

    articles = collect_news()

    print(
        "Collected "
        + str(len(articles))
        + " articles."
    )

    unique_articles = []

    for article in articles:

        if not is_duplicate(
            article,
            unique_articles
        ):

            unique_articles.append(
                article
            )

    print(
        "After duplicate filter: "
        + str(
            len(unique_articles)
        )
    )

    sent = 0

    for article in unique_articles:

        symbol = article.get(
            "symbol",
            "CRYPTO"
        )

        unique = (
            symbol
            + "|"
            + article.get(
                "title",
                ""
            )
            + "|"
            + article.get(
                "link",
                ""
            )
        )

        news_id = make_id(
            unique
        )

        if news_id in seen:

            continue

        score = importance_score(
            article.get(
                "title",
                ""
            ),
            article.get(
                "source",
                ""
            ),
            article.get(
                "type",
                "news"
            )
        )

        if score < 3:

            print(
                "Skipped low importance: "
                + symbol
            )

            seen.add(
                news_id
            )

            continue

        message = build_message(
            symbol,
            article
        )

        result = send_telegram(
            message
        )

        if result:

            seen.add(
                news_id
            )

            sent += 1

            print(
                "Sent: "
                + symbol
                + " | "
                + article.get(
                    "source",
                    ""
                )
            )

        time.sleep(1)

    save_seen(
        seen
    )

    print(
        "Finished. Sent "
        + str(sent)
        + " new articles."
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
