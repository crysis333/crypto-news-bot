import os
import json
import hashlib
import time
import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEEN_FILE = "seen_news.json"
START_FILE = "bot_initialized.txt"

# چند سرور رایگان LibreTranslate برای پشتیبان
TRANSLATION_SERVERS = [
    "https://de.libretranslate.com/translate",
    "https://translate.mentality.rip/translate",
    "https://translate.argosopentech.com/translate",
]


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

BLOCKED_SOURCES = [
    "bybit.com",
    "binance.com",
    "kraken.com",
    "okx.com",
    "kucoin.com",
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


# ============================================================
# HTTP
# ============================================================

def fetch_url(url, timeout=20):

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 (compatible; CryptoNewsBot/8.0)"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            return response.read()

    except Exception as error:

        print("Fetch error:", url, error)

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

            return set(json.load(file))

    except Exception:

        return set()


def save_seen(seen):

    try:

        with open(
            SEEN_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                list(seen)[-5000:],
                file,
                ensure_ascii=False
            )

    except Exception as error:

        print("Save error:", error)


def make_id(text):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    text = html.unescape(
        text or ""
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize(text):

    return clean_text(text).lower()


# ============================================================
# ARTICLE FILTER
# ============================================================

def blocked_article(article):

    title = normalize(
        article.get("title", "")
    )

    source = normalize(
        article.get("source", "")
    )

    combined = title + " " + source

    for word in BLOCKED_WORDS:

        if word in combined:
            return True

    for source_name in BLOCKED_SOURCES:

        if source_name in source:
            return True

    return False


def valid_news(title):

    text = normalize(title)

    return any(
        keyword in text
        for keyword in NEWS_KEYWORDS
    )


# ============================================================
# GOOGLE NEWS
# ============================================================

def google_news(query):

    url = (
        "https://news.google.com/rss/search?"
        "q="
        + urllib.parse.quote(query)
        + "&hl=en-US&gl=US&ceid=US:en"
    )

    data = fetch_url(url)

    if not data:
        return []

    try:

        root = ET.fromstring(data)

        results = []

        for item in root.findall(
            "./channel/item"
        )[:30]:

            title = clean_text(
                item.findtext(
                    "title",
                    ""
                )
            )

            link = clean_text(
                item.findtext(
                    "link",
                    ""
                )
            )

            pubdate = clean_text(
                item.findtext(
                    "pubDate",
                    ""
                )
            )

            source_node = item.find(
                "source"
            )

            source = ""

            if source_node is not None:
                source = clean_text(
                    source_node.text or ""
                )

            article = {
                "title": title,
                "link": link,
                "date": pubdate,
                "source": source,
                "type": "news",
            }

            if not blocked_article(article):
                results.append(article)

        return results

    except Exception as error:

        print("Google News parse error:", error)

        return []


# ============================================================
# REDDIT
# ============================================================

def reddit_news(subreddit):

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

        results = []

        for entry in root.findall(
            "atom:entry",
            namespace
        )[:20]:

            title = clean_text(
                entry.findtext(
                    "atom:title",
                    "",
                    namespace
                )
            )

            updated = clean_text(
                entry.findtext(
                    "atom:updated",
                    "",
                    namespace
                )
            )

            link_node = entry.find(
                "atom:link",
                namespace
            )

            link = ""

            if link_node is not None:

                link = link_node.attrib.get(
                    "href",
                    ""
                )

            results.append({
                "title": title,
                "link": link,
                "date": updated,
                "source":
                    "Reddit / r/"
                    + subreddit,
                "type": "reddit",
            })

        return results

    except Exception as error:

        print("Reddit parse error:", error)

        return []


# ============================================================
# COIN MATCH
# ============================================================

def matches_coin(
    symbol,
    project,
    article
):

    if blocked_article(article):
        return False

    title = normalize(
        article.get("title", "")
    )

    if re.search(
        r"\b"
        + re.escape(symbol.lower())
        + r"\b",
        title
    ):
        return True

    words = project.lower().split()

    for word in words:

        if len(word) >= 4 and word in title:
            return True

    return False


# ============================================================
# LIBRETRANSLATE
# ============================================================

def libre_translate(text):

    text = clean_text(text)

    if not text:
        return ""

    for server in TRANSLATION_SERVERS:

        try:

            payload = json.dumps({
                "q": text,
                "source": "en",
                "target": "fa",
                "format": "text",
            }).encode("utf-8")

            request = urllib.request.Request(
                server,
                data=payload,
                headers={
                    "Content-Type":
                        "application/json",
                    "User-Agent":
                        "CryptoNewsBot/8.0",
                },
                method="POST",
            )

            with urllib.request.urlopen(
                request,
                timeout=25
            ) as response:

                raw = response.read().decode(
                    "utf-8"
                )

                data = json.loads(raw)

                translated = data.get(
                    "translatedText",
                    ""
                )

                if translated:

                    return clean_text(
                        translated
                    )

        except Exception as error:

            print(
                "Translation server failed:",
                server,
                error
            )

        time.sleep(1)

    return ""


# ============================================================
# CRYPTO GLOSSARY
# ============================================================

GLOSSARY = {

    "استیبل کوین": "استیبل‌کوین",
    "استیبل کوین‌ها": "استیبل‌کوین‌ها",

    "توکن باز کردن قفل": "آزادسازی توکن",
    "باز کردن قفل توکن": "آزادسازی توکن",

    "نهنگ ها": "نهنگ‌ها",
    "نهنگ": "نهنگ",

    "انباشت": "انباشت",
    "انباشت کردن": "انباشت",

    "شکست": "شکست",
    "شکست مقاومت": "شکست مقاومت",

    "فروش": "فروش",
    "فشار فروش": "فشار فروش",

    "حجم": "حجم معاملات",

    "شبکه اصلی": "مین‌نت",
    "شبکه آزمایشی": "تست‌نت",

    "ایردراپ": "ایردراپ",

    "سهام": "استیکینگ",

    "ارزش بازار": "ارزش بازار",

    "ورودی": "ورود سرمایه",
    "خروجی": "خروج سرمایه",

    "صعودی": "صعودی",
    "نزولی": "نزولی",
}


def apply_glossary(text):

    result = clean_text(text)

    for old, new in GLOSSARY.items():

        result = result.replace(
            old,
            new
        )

    return result


# ============================================================
# FORCE PROJECT NAME
# ============================================================

def improve_project_name(
    symbol,
    translated
):

    project = PROJECT_NAMES.get(
        symbol,
        symbol
    )

    # اگر مترجم نام پروژه را خراب کرد،
    # نام صحیح پروژه را وارد می‌کنیم.

    translated = re.sub(
        r"\b"
        + re.escape(symbol)
        + r"\b",
        symbol,
        translated,
        flags=re.IGNORECASE
    )

    return translated


# ============================================================
# SMART TRANSLATION
# ============================================================

def translate_title(
    symbol,
    original
):

    original = clean_text(
        original
    )

    translated = libre_translate(
        original
    )

    if not translated:

        return ""

    translated = apply_glossary(
        translated
    )

    translated = improve_project_name(
        symbol,
        translated
    )

    # حذف ترجمه‌های خراب که هنوز بخش بزرگی
    # از متن انگلیسی هستند.

    english_words = re.findall(
        r"\b[A-Za-z]{4,}\b",
        translated
    )

    total_words = max(
        1,
        len(translated.split())
    )

    english_ratio = (
        len(english_words)
        / total_words
    )

    if english_ratio > 0.45:

        print(
            "Translation rejected:",
            translated
        )

        return ""

    return translated


# ============================================================
# FALLBACK TITLES
# ============================================================

def fallback_title(
    symbol,
    original
):

    text = normalize(
        original
    )

    project = PROJECT_NAMES.get(
        symbol,
        symbol
    )

    percent_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        original
    )

    percent = ""

    if percent_match:

        percent = (
            percent_match.group(1)
            + "%"
        )

    if (
        "whale" in text
        and "accumulate" in text
    ):

        return (
            "نهنگ‌ها در حال انباشت "
            + symbol
            + " هستند"
        )

    if (
        "whale" in text
        and (
            "sell" in text
            or "selling" in text
        )
    ):

        return (
            "نهنگ‌ها در حال فروش "
            + symbol
            + " هستند"
        )

    if (
        "unlock" in text
        and "token" in text
    ):

        return (
            "آزادسازی توکن‌های "
            + symbol
            + " در کانون توجه بازار قرار گرفت"
        )

    if (
        "surge" in text
        or "rally" in text
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
        "drop" in text
        or "decline" in text
        or "fall" in text
        or "plunge" in text
    ):

        if percent:

            return (
                project
                + " "
                + percent
                + " افت کرد"
            )

        return (
            project
            + " با کاهش قیمت مواجه شد"
        )

    if "partnership" in text:

        return (
            project
            + " از یک همکاری جدید خبر داد"
        )

    if "hack" in text or "exploit" in text:

        return (
            "هشدار امنیتی درباره "
            + project
        )

    if "listing" in text or "listed" in text:

        return (
            project
            + " در یک صرافی یا بازار جدید لیست شد"
        )

    if "upgrade" in text:

        return (
            "ارتقای جدید "
            + project
            + " منتشر شد"
        )

    if "mainnet" in text:

        return (
            "تحولات جدیدی در مین‌نت "
            + project
        )

    return (
        "خبر جدید درباره "
        + project
    )


# ============================================================
# SENTIMENT
# ============================================================

POSITIVE = [
    "surge",
    "rally",
    "bullish",
    "growth",
    "gain",
    "gains",
    "increase",
    "increases",
    "partnership",
    "adoption",
    "approval",
    "approved",
    "breakout",
    "breakthrough",
    "record",
    "launch",
    "upgrade",
    "funding",
    "investment",
]


NEGATIVE = [
    "hack",
    "hacked",
    "exploit",
    "exploited",
    "attack",
    "crash",
    "collapse",
    "drop",
    "drops",
    "decline",
    "declines",
    "plunge",
    "sell",
    "selling",
    "lawsuit",
    "ban",
    "banned",
    "delist",
    "delisted",
]


def sentiment(title):

    text = normalize(title)

    positive = sum(
        1
        for word in POSITIVE
        if word in text
    )

    negative = sum(
        1
        for word in NEGATIVE
        if word in text
    )

    if positive > negative:
        return "🟢 مثبت"

    if negative > positive:
        return "🔴 منفی"

    return "🟡 خنثی"


# ============================================================
# IMPORTANCE
# ============================================================

IMPORTANT = {
    "hack": 7,
    "hacked": 7,
    "exploit": 7,
    "exploit": 7,
    "etf": 5,
    "approval": 5,
    "approved": 5,
    "lawsuit": 4,
    "ban": 5,
    "banned": 5,
    "delisting": 5,
    "mainnet": 4,
    "security": 4,
    "partnership": 3,
    "upgrade": 3,
    "launch": 3,
    "listing": 3,
    "funding": 3,
    "investment": 3,
    "unlock": 3,
    "whale": 2,
    "whales": 2,
    "accumulate": 3,
    "accumulation": 3,
    "breakout": 3,
}


def importance(title):

    text = normalize(title)

    score = 3

    for word, value in IMPORTANT.items():

        if word in text:
            score += value

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
# TELEGRAM
# ============================================================

def send_telegram(message):

    url = (
        "https://api.telegram.org/bot"
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
        },
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

        return ""


# ============================================================
# MESSAGE
# ============================================================

def build_message(
    symbol,
    article
):

    original = clean_text(
        article.get(
            "title",
            ""
        )
    )

    translated = translate_title(
        symbol,
        original
    )

    if not translated:

        translated = fallback_title(
            symbol,
            original
        )

    score = importance(
        original
    )

    impact = sentiment(
        original
    )

    source = article.get(
        "source",
        "Unknown"
    )

    return (
        "📰 "
        + symbol
        + " | "
        + importance_label(score)
        + "\n"
        "🔹 "
        + translated
        + "\n"
        "📊 اهمیت: "
        + str(score)
        + "/10\n"
        "📈 تأثیر احتمالی: "
        + impact
        + "\n"
        "🇬🇧 Original: "
        + original
        + "\n"
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

def collect():

    articles = []

    for symbol, project in COINS.items():

        print(
            "Google News -> "
            + symbol
        )

        news = google_news(
            project
            + " crypto"
        )

        for article in news:

            if matches_coin(
                symbol,
                project,
                article
            ):

                article["symbol"] = symbol

                articles.append(
                    article
                )

    for subreddit in REDDIT_SUBREDDITS:

        print(
            "Reddit -> r/"
            + subreddit
        )

        news = reddit_news(
            subreddit
        )

        for article in news:

            for symbol, project in COINS.items():

                if matches_coin(
                    symbol,
                    project,
                    article
                ):

                    article["symbol"] = symbol

                    articles.append(
                        article
                    )

                    break

    return articles


# ============================================================
# FIRST RUN
# ============================================================

def first_run():

    print(
        "First run detected."
    )

    print(
        "Old news will be ignored."
    )

    articles = collect()

    seen = load_seen()

    for article in articles:

        key = (
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
            make_id(key)
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

        first_run()

        return

    print(
        "Collecting new crypto news..."
    )

    articles = collect()

    print(
        "Collected "
        + str(len(articles))
        + " articles."
    )

    sent = 0

    processed = set()

    for article in articles:

        symbol = article.get(
            "symbol",
            ""
        )

        title = article.get(
            "title",
            ""
        )

        link = article.get(
            "link",
            ""
        )

        key = (
            symbol
            + "|"
            + title
            + "|"
            + link
        )

        news_id = make_id(key)

        if news_id in seen:
            continue

        if news_id in processed:
            continue

        processed.add(
            news_id
        )

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
                "Sent -> "
                + symbol
            )

        time.sleep(2)

    save_seen(seen)

    print(
        "Finished."
    )

    print(
        "Sent: "
        + str(sent)
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
