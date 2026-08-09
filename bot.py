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
    "WINK": "WINkLink crypto",
    "BTC": "Bitcoin BTC crypto",
    "ETH": "Ethereum ETH crypto",
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
# SOURCES / FILTERS
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
    "price prediction calculator",
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
}


# ============================================================
# CRYPTO TERMINOLOGY
# ============================================================

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

    "network upgrade":
        "ارتقای شبکه",

    "partnership":
        "همکاری",

    "partnerships":
        "همکاری‌ها",

    "integration":
        "ادغام",

    "integrated":
        "ادغام شد",

    "listing":
        "لیست شدن",

    "listed":
        "لیست شد",

    "delisting":
        "حذف از لیست",

    "delisted":
        "از لیست خارج شد",

    "hack":
        "هک",

    "hacked":
        "هک شد",

    "exploit":
        "اکسپلویت",

    "exploited":
        "مورد سوءاستفاده قرار گرفت",

    "vulnerability":
        "آسیب‌پذیری",

    "security breach":
        "نقض امنیتی",

    "lawsuit":
        "دادخواست حقوقی",

    "regulatory":
        "قانون‌گذاری",

    "regulation":
        "مقررات",

    "adoption":
        "پذیرش",

    "roadmap":
        "نقشه راه",

    "proposal":
        "پیشنهاد حاکمیتی",

    "vote":
        "رأی‌گیری",

    "rally":
        "رالی صعودی",

    "surge":
        "جهش",

    "sell-off":
        "فشار فروش",

    "selloff":
        "فشار فروش",

    "bullish":
        "صعودی",

    "bearish":
        "نزولی",

    "breakout":
        "شکست مقاومت",

    "all-time high":
        "بالاترین قیمت تاریخی",

    "all time high":
        "بالاترین قیمت تاریخی",

    "all-time low":
        "پایین‌ترین قیمت تاریخی",

    "supply":
        "عرضه",

    "demand":
        "تقاضا",

    "circulating supply":
        "عرضه در گردش",

    "transaction":
        "تراکنش",

    "transactions":
        "تراکنش‌ها",

    "developers":
        "توسعه‌دهندگان",

    "developer":
        "توسعه‌دهنده",

    "ecosystem":
        "اکوسیستم",
}


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(text):
    text = html.unescape(text or "")
    text = text.lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(
        r"[^a-z0-9\u0600-\u06ff\s]",
        " ",
        text
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def make_id(text):
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def similarity(a, b):
    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b)
    ).ratio()


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
            return set(json.load(file))

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
                    "(compatible; CryptoNewsBot/6.0)"
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
# QUALITY FILTER
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


def is_quality_news(article):

    if is_blocked_article(article):
        return False

    title = article.get(
        "title",
        ""
    ).lower()

    return any(
        word in title
        for word in NEWS_KEYWORDS
    )


# ============================================================
# GOOGLE NEWS
# ============================================================

def get_google_news(query):

    encoded = urllib.parse.quote(query)

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

        root = ET.fromstring(data)

        articles = []

        for item in root.findall(
            "./channel/item"
        )[:20]:

            title = item.findtext(
                "title",
                ""
            )

            link = item.findtext(
                "link",
                ""
            )

            pub_date = item.findtext(
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
                "date": pub_date.strip(),
                "source": source.strip(),
                "type": "news",
            }

            if is_quality_news(article):
                articles.append(article)

        return articles

    except Exception as error:

        print(
            "Google RSS error:",
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

        root = ET.fromstring(data)

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
            "Reddit RSS error:",
            error
        )

        return []


# ============================================================
# COIN MATCHING
# ============================================================

def article_matches_coin(
    symbol,
    query,
    article
):

    title = article.get(
        "title",
        ""
    ).lower()

    source = article.get(
        "source",
        ""
    ).lower()

    text = title + " " + source

    if is_blocked_article(article):
        return False

    if not any(
        word in title
        for word in NEWS_KEYWORDS
    ):
        return False

    if symbol == "BTC":

        return (
            "bitcoin" in text
            or bool(
                re.search(
                    r"\bbtc\b",
                    text
                )
            )
        )

    if symbol == "ETH":

        return (
            "ethereum" in text
            or bool(
                re.search(
                    r"\beth\b",
                    text
                )
            )
        )

    if re.search(
        r"\b"
        + re.escape(symbol.lower())
        + r"\b",
        text
    ):
        return True

    query_words = query.lower().split()

    for word in query_words:

        if (
            len(word) >= 4
            and word not in [
                "crypto",
                "token",
                "network",
                "blockchain",
            ]
            and word in text
        ):
            return True

    return False


# ============================================================
# TRANSLATION
# ============================================================

def protect_crypto_terms(text):

    protected = {}
    counter = 0

    terms = sorted(
        CRYPTO_TERMS.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    result = text

    for english, persian in terms:

        pattern = (
            r"(?<![A-Za-z])"
            + re.escape(english)
            + r"(?![A-Za-z])"
        )

        while True:

            match = re.search(
                pattern,
                result,
                flags=re.IGNORECASE
            )

            if not match:
                break

            key = (
                "__CRYPTO_TERM_"
                + str(counter)
                + "__"
            )

            protected[key] = persian

            result = (
                result[:match.start()]
                + key
                + result[match.end():]
            )

            counter += 1

    return result, protected


def restore_crypto_terms(
    text,
    protected
):

    result = text

    for key, value in protected.items():

        result = result.replace(
            key,
            value
        )

    return result


def improve_persian_title(title):

    result = title.strip()

    replacements = {

        "افزایش می یابد":
            "افزایش یافت",

        "افزایش می‌دهد":
            "افزایش یافت",

        "افزایش می دهد":
            "افزایش یافت",

        "کاهش می یابد":
            "کاهش یافت",

        "کاهش می‌دهد":
            "کاهش یافت",

        "کاهش می دهد":
            "کاهش یافت",

        "در روایت های قوی":
            "در بحبوحه تقویت روایت‌های صعودی",

        "روایت های قوی":
            "روایت‌های صعودی",

        "روایت قوی":
            "روایت صعودی",

        "افزایش":
            "رشد",

        "سرمایه گذاران":
            "سرمایه‌گذاران",

        "توسعه دهندگان":
            "توسعه‌دهندگان",

        "ارز رمزنگاری شده":
            "ارز دیجیتال",

        "ارز رمزنگاری":
            "ارز دیجیتال",

        "بازار رمزنگاری":
            "بازار کریپتو",

        "بلاک چین":
            "بلاک‌چین",

        "بلاکچین":
            "بلاک‌چین",

        "نعناع":
            "ایجاد توکن",

        "سوختگی":
            "سوزاندن",

        "سوختن":
            "سوزاندن",

        "شبکه پولکادوت":
            "پولکادات",

        "شبکه اتریوم":
            "اتریوم",

        "شبکه بیت کوین":
            "بیت‌کوین",

        "بیت کوین":
            "بیت‌کوین",

        "قیمت ارز دیجیتال":
            "قیمت ارز",

        "توکن رمزنگاری":
            "توکن کریپتویی",
    }

    for old, new in replacements.items():
        result = result.replace(
            old,
            new
        )

    result = re.sub(
        r"\s+([،,:؛.!؟])",
        r"\1",
        result
    )

    result = re.sub(
        r"\s+",
        " ",
        result
    )

    return result.strip()


def translate_to_persian(text):

    prepared, protected = (
        protect_crypto_terms(text)
    )

    try:

        encoded = urllib.parse.quote(
            prepared
        )

        url = (
            "https://translate.googleapis.com/"
            "translate_a/single"
            "?client=gtx"
            "&sl=auto"
            "&tl=fa"
            "&dt=t"
            "&q="
            + encoded
        )

        data = fetch_url(
            url,
            timeout=15
        )

        if not data:

            translated = prepared

        else:

            result = json.loads(
                data.decode("utf-8")
            )

            translated = ""

            for part in result[0]:

                if part and part[0]:
                    translated += part[0]

    except Exception as error:

        print(
            "Translation error:",
            error
        )

        translated = prepared

    translated = restore_crypto_terms(
        translated,
        protected
    )

    return improve_persian_title(
        translated
    )


# ============================================================
# SENTIMENT
# ============================================================

def analyze_sentiment(title):

    text = normalize_text(title)

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
        "surge" in text
        or "rally" in text
        or "breakout" in text
    ):
        score += 1

    if (
        "hack" in text
        or "exploit" in text
        or "etf" in text
        or "approval" in text
        or "lawsuit" in text
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
# DUPLICATES
# ============================================================

def is_duplicate(
    article,
    recent_articles
):

    title = article.get(
        "title",
        ""
    )

    link = article.get(
        "link",
        ""
    )

    for old in recent_articles:

        if (
            link
            and link == old.get(
                "link",
                ""
            )
        ):
            return True

        if similarity(
            title,
            old.get(
                "title",
                ""
            )
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
        "disable_web_page_preview": "false",
    }).encode("utf-8")

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
# TELEGRAM MESSAGE
# ============================================================

def build_message(
    symbol,
    article
):

    original_title = html.unescape(
        article.get(
            "title",
            ""
        )
    ).strip()

    persian_title = (
        translate_to_persian(
            original_title
        )
    )

    source = article.get(
        "source",
        ""
    )

    if not source:
        source = "Unknown"

    sentiment = analyze_sentiment(
        original_title
    )

    score = importance_score(
        original_title,
        source,
        article.get(
            "type",
            "news"
        )
    )

    level = importance_label(
        score
    )

    return (
        "📰 "
        + symbol
        + " | "
        + level
        + "\n\n"
        "🔹 "
        + persian_title
        + "\n\n"
        "📊 اهمیت: "
        + str(score)
        + "/10\n"
        "📈 تأثیر احتمالی: "
        + sentiment
        + "\n\n"
        "🇬🇧 Original:\n"
        + original_title
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
# COLLECT NEWS
# ============================================================

def collect_news():

    all_articles = []

    for symbol, query in COINS.items():

        print(
            "Google News -> "
            + symbol
        )

        articles = get_google_news(
            query
        )

        for article in articles:

            if article_matches_coin(
                symbol,
                query,
                article
            ):

                article["symbol"] = symbol

                all_articles.append(
                    article
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

            for symbol, query in COINS.items():

                if article_matches_coin(
                    symbol,
                    query,
                    article
                ):

                    new_article = dict(
                        article
                    )

                    new_article["symbol"] = (
                        symbol
                    )

                    all_articles.append(
                        new_article
                    )

                    break

    return all_articles


# ============================================================
# FIRST RUN
# ============================================================

def initialize_bot():

    seen = load_seen()

    print(
        "First run detected."
    )

    print(
        "Old news will be ignored."
    )

    articles = collect_news()

    for article in articles:

        symbol = article.get(
            "symbol",
            ""
        )

        unique_text = (
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

        seen.add(
            make_id(unique_text)
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
        + str(len(unique_articles))
    )

    new_count = 0

    for article in unique_articles:

        symbol = article.get(
            "symbol",
            "CRYPTO"
        )

        unique_text = (
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
            unique_text
        )

        if news_id in seen:
            continue

        seen.add(news_id)

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

        if score <= 2:

            print(
                "Skipped low importance: "
                + symbol
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

            print(
                "Sent: "
                + symbol
                + " | "
                + article.get(
                    "source",
                    ""
                )
            )

            new_count += 1

        time.sleep(1)

    save_seen(seen)

    print(
        "Finished. Sent "
        + str(new_count)
        + " new articles."
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
