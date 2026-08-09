import os
import json
import hashlib
import time
import html
import re
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

SEEN_FILE = "seen_news.json"
START_FILE = "bot_initialized.txt"

# مدل رایگان/کم‌هزینه Gemini
GEMINI_MODEL = "gemini-2.5-flash"


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
# PERSIAN PROJECT NAMES
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
    "TIA": "سلستیا",
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
# BAD / LOW VALUE NEWS FILTER
# ============================================================

BLOCKED_PHRASES = [
    "calculator",
    "converter",
    "convert",
    "conversion",
    "currency converter",
    "price converter",
    "exchange rate",
    "how much is",
    "to usd",
    "to eur",
    "usd to",
    "eur to",
    "btc to usd",
    "eth to usd",
]


BLOCKED_SOURCES = [
    "bybit.com",
    "binance.com",
    "kraken.com",
    "okx.com",
    "kucoin.com",
]


# ============================================================
# IMPORTANT NEWS KEYWORDS
# ============================================================

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
    "responds",
    "response",
    "critic",
    "criticism",
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
                    "Mozilla/5.0 (compatible; CryptoNewsBot/9.0)"
            },
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

        print(
            "Save error:",
            error
        )


def make_id(text):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================
# TEXT
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

    return clean_text(
        text
    ).lower()


# ============================================================
# ARTICLE FILTER
# ============================================================

def blocked_article(article):

    title = normalize(
        article.get(
            "title",
            ""
        )
    )

    source = normalize(
        article.get(
            "source",
            ""
        )
    )

    combined = (
        title
        + " "
        + source
    )

    for phrase in BLOCKED_PHRASES:

        if phrase in combined:
            return True

    for source_name in BLOCKED_SOURCES:

        if source_name in source:
            return True

    return False


def valid_news(title):

    text = normalize(
        title
    )

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

    data = fetch_url(
        url
    )

    if not data:
        return []

    try:

        root = ET.fromstring(
            data
        )

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

            if blocked_article(
                article
            ):
                continue

            results.append(
                article
            )

        return results

    except Exception as error:

        print(
            "Google News parse error:",
            error
        )

        return []


# ============================================================
# REDDIT
# ============================================================

def reddit_news(
    subreddit
):

    url = (
        "https://www.reddit.com/r/"
        + subreddit
        + "/new/.rss"
    )

    data = fetch_url(
        url
    )

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

        print(
            "Reddit parse error:",
            error
        )

        return []


# ============================================================
# COIN MATCH
# ============================================================

def matches_coin(
    symbol,
    project,
    article
):

    if blocked_article(
        article
    ):
        return False

    title = normalize(
        article.get(
            "title",
            ""
        )
    )

    symbol_match = re.search(
        r"\b"
        + re.escape(
            symbol.lower()
        )
        + r"\b",
        title
    )

    if symbol_match:
        return True

    project_words = (
        project.lower()
        .split()
    )

    for word in project_words:

        if (
            len(word) >= 4
            and word in title
        ):
            return True

    return False


# ============================================================
# GEMINI TRANSLATION
# ============================================================

def gemini_translate(
    symbol,
    original
):

    original = clean_text(
        original
    )

    if not original:
        return None

    prompt = f"""
تو یک ویراستار حرفه‌ای اخبار ارز دیجیتال هستی.

عنوان انگلیسی زیر را به فارسی طبیعی، روان و خبری ترجمه کن.

قوانین بسیار مهم:

1. معنی کامل عنوان را منتقل کن.
2. ترجمه تحت‌اللفظی و ماشینی نباشد.
3. عنوان باید مثل تیتر یک رسانه فارسی حوزه کریپتو نوشته شود.
4. نام پروژه‌ها و ارزها را درست نگه دار.
5. نماد ارز {symbol} را همیشه به صورت {symbol} بنویس.
6. اصطلاحات کریپتو را درست ترجمه کن:
   whale = نهنگ
   whales = نهنگ‌ها
   accumulate = انباشت کردن
   accumulation = انباشت
   token unlock = آزادسازی توکن
   stablecoin = استیبل‌کوین
   breakout = شکست مقاومت
   sell-off = موج فروش
   inflows = ورود سرمایه
   outflows = خروج سرمایه
   rally = رشد / رالی
   surge = جهش
   plunge = سقوط شدید
   outlook = چشم‌انداز
   criticism = انتقاد
   responds to criticism = به انتقادها واکنش نشان داد
7. اگر عنوان درباره قیمت است، قیمت را درست منتقل کن.
8. درصدها و اعداد را حذف نکن.
9. نام رسانه را داخل تیتر نیاور، مگر اینکه برای معنی ضروری باشد.
10. هیچ توضیح اضافه‌ای نده.
11. فقط یک تیتر فارسی خروجی بده.
12. اگر جمله انگلیسی از نظر خبری ضعیف است، آن را به یک تیتر فارسی طبیعی تبدیل کن، اما معنی را تغییر نده.

نمونه:

English:
Wall Street Giant Responds to Criticism About Dogecoin (DOGE)

Correct Persian:
غول وال‌استریت به انتقادها درباره دوج‌کوین (DOGE) واکنش نشان داد

English:
EigenLayer whales accumulate EIGEN tokens post-transfer unlock despite price lag

Correct Persian:
نهنگ‌های EigenLayer پس از آزادسازی توکن‌های EIGEN، با وجود ضعف قیمت، به انباشت ادامه دادند

English:
Stablecoin Boom Fuels Recovery Hopes for Near Protocol

Correct Persian:
رونق استیبل‌کوین‌ها امید به بهبود وضعیت NEAR Protocol را افزایش داده است

عنوانی که باید ترجمه شود:

{original}
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/"
        + GEMINI_MODEL
        + ":generateContent?key="
        + urllib.parse.quote(
            GEMINI_API_KEY
        )
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 200,
        }
    }

    try:

        body = json.dumps(
            payload
        ).encode(
            "utf-8"
        )

        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type":
                    "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        data = json.loads(
            raw
        )

        candidates = data.get(
            "candidates",
            []
        )

        if not candidates:
            print(
                "Gemini returned no candidates."
            )
            return None

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        if not parts:
            return None

        translated = parts[0].get(
            "text",
            ""
        )

        translated = clean_text(
            translated
        )

        # حذف احتمالی markdown
        translated = re.sub(
            r"^#+\s*",
            "",
            translated
        )

        translated = translated.strip(
            "\"'«»"
        )

        if not translated:
            return None

        return translated

    except urllib.error.HTTPError as error:

        try:
            detail = error.read().decode(
                "utf-8"
            )
        except Exception:
            detail = ""

        print(
            "Gemini HTTP error:",
            error.code,
            detail[:500]
        )

        return None

    except Exception as error:

        print(
            "Gemini translation error:",
            error
        )

        return None


# ============================================================
# TRANSLATION QUALITY CHECK
# ============================================================

def translation_is_good(
    original,
    translated,
    symbol
):

    if not translated:
        return False

    # ترجمه نباید تقریباً همان متن انگلیسی باشد
    if normalize(
        original
    ) == normalize(
        translated
    ):
        return False

    # حداقل طول منطقی
    if len(translated) < 15:
        return False

    # اگر هنوز مقدار زیادی انگلیسی باقی مانده باشد
    english_words = re.findall(
        r"\b[A-Za-z]{4,}\b",
        translated
    )

    words = translated.split()

    if len(words) >= 5:

        ratio = (
            len(english_words)
            / len(words)
        )

        if ratio > 0.55:
            return False

    # متن‌های خراب معمولاً این‌ها را دارند
    bad_patterns = [
        "خبر جدید درباره",
        "ترجمه",
        "translation",
        "unable",
        "cannot",
        "i cannot",
        "i'm sorry",
    ]

    lower = normalize(
        translated
    )

    for pattern in bad_patterns:

        if pattern in lower:
            return False

    return True


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
    "accumulate",
    "accumulation",
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
    "security",
]


def sentiment(
    title
):

    text = normalize(
        title
    )

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
    "attack": 7,
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
    "record": 3,
    "surge": 2,
    "rally": 2,
}


def importance(
    title
):

    text = normalize(
        title
    )

    score = 3

    for word, value in IMPORTANT.items():

        if word in text:
            score += value

    return max(
        1,
        min(score, 10)
    )


def importance_label(
    score
):

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

def send_telegram(
    message
):

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
    article,
    translated
):

    original = clean_text(
        article.get(
            "title",
            ""
        )
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
        + importance_label(
            score
        )
        + "\n\n"
        "🔹 "
        + translated
        + "\n\n"
        "📊 اهمیت: "
        + str(score)
        + "/10\n"
        "📈 تأثیر احتمالی: "
        + impact
        + "\n\n"
        "🇬🇧 Original: "
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

                # فقط خبرهای واقعی
                # نه تبدیل قیمت و ماشین حساب
                if not valid_news(
                    article.get(
                        "title",
                        ""
                    )
                ):
                    continue

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
            make_id(
                key
            )
        )

    save_seen(
        seen
    )

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

        news_id = make_id(
            key
        )

        if news_id in seen:
            continue

        if news_id in processed:
            continue

        processed.add(
            news_id
        )

        print(
            "Translating -> "
            + symbol
            + " -> "
            + title
        )

        translated = gemini_translate(
            symbol,
            title
        )

        if not translation_is_good(
            title,
            translated,
            symbol
        ):

            print(
                "Translation rejected -> "
                + symbol
            )

            # خبر را seen نمی‌کنیم
            # تا در اجرای بعدی دوباره
            # امکان ترجمه داشته باشد.
            continue

        message = build_message(
            symbol,
            article,
            translated
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

        time.sleep(
            2
        )

    save_seen(
        seen
    )

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
