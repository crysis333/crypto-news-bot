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
    "WINK": "WINkLink crypto WIN",
    "BTC": "Bitcoin BTC crypto",
    "ETH": "Ethereum ETH crypto",
}


# ============================================================
# REDDIT SOURCES
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
# GENERAL HELPERS
# ============================================================

def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text):
    """
    برای تشخیص اخبار تکراری.
    """
    text = html.unescape(text or "")
    text = text.lower()

    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-z0-9\u0600-\u06ff\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def similarity(a, b):
    return SequenceMatcher(
        None,
        normalize_text(a),
        normalize_text(b)
    ).ratio()


# ============================================================
# SEEN NEWS
# ============================================================

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))

    except Exception as e:
        print("Seen file error:", e)
        return set()


def save_seen(seen):
    try:
        # فقط 5000 مورد آخر
        data = list(seen)[-5000:]

        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False
            )

    except Exception as e:
        print("Save seen error:", e)


# ============================================================
# HTTP
# ============================================================

def fetch_url(url, timeout=20):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 (compatible; CryptoNewsBot/2.0)"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            return response.read()

    except Exception as e:
        print("Fetch error:", url, e)
        return None


# ============================================================
# GOOGLE NEWS RSS
# ============================================================

def get_google_news(query):
    encoded = urllib.parse.quote(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded}"
        "&hl=en-US"
        "&gl=US"
        "&ceid=US:en"
    )

    data = fetch_url(url)

    if not data:
        return []

    try:
        root = ET.fromstring(data)

        results = []

        for item in root.findall("./channel/item")[:15]:

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")

            source = item.find("source")

            source_name = ""

            if source is not None:
                source_name = source.text or ""

            results.append({
                "title": title.strip(),
                "link": link.strip(),
                "date": pub_date.strip(),
                "source": source_name.strip(),
                "type": "news"
            })

        return results

    except Exception as e:
        print("Google RSS error:", e)
        return []


# ============================================================
# REDDIT RSS
# ============================================================

def get_reddit(subreddit):

    url = (
        f"https://www.reddit.com/r/"
        f"{subreddit}/new/.rss"
    )

    data = fetch_url(url)

    if not data:
        return []

    try:
        root = ET.fromstring(data)

        namespace = {
            "atom": "http://www.w3.org/2005/Atom"
        }

        results = []

        entries = root.findall(
            "atom:entry",
            namespace
        )[:15]

        for entry in entries:

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

            results.append({
                "title": title.strip(),
                "link": link.strip(),
                "date": updated.strip(),
                "source": f"Reddit / r/{subreddit}",
                "type": "reddit"
            })

        return results

    except Exception as e:
        print(
            f"Reddit RSS error ({subreddit}):",
            e
        )

        return []


# ============================================================
# COIN DETECTION
# ============================================================

def article_matches_coin(symbol, query, article):
    text = (
        article.get("title", "")
        + " "
        + article.get("source", "")
    ).lower()

    symbol_lower = symbol.lower()

    # نام کامل پروژه
    words = query.lower().split()

    # BTC و ETH
    if symbol == "BTC":
        if (
            "bitcoin" in text
            or "btc" in text
        ):
            return True

    if symbol == "ETH":
        if (
            "ethereum" in text
            or re.search(r"\beth\b", text)
        ):
            return True

    # نماد
    if re.search(
        rf"\b{re.escape(symbol_lower)}\b",
        text
    ):
        return True

    # نام پروژه
    important_words = [
        w for w in words
        if len(w) >= 4
        and w not in {
            "crypto",
            "token",
            "network",
            "blockchain"
        }
    ]

    for word in important_words:
        if word in text:
            return True

    return False


# ============================================================
# SENTIMENT
# ============================================================

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
    "shutdown",
    "delist",
    "delisted",
    "warning",
    "investigation",
    "investigated",
]


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
# IMPORTANCE SCORE
# ============================================================

IMPORTANT_WORDS = {
    "hack": 5,
    "hacked": 5,
    "exploit": 5,
    "exploit": 5,
    "approval": 4,
    "approved": 4,
    "lawsuit": 4,
    "ban": 5,
    "banned": 5,
    "listing": 3,
    "delisting": 5,
    "delisted": 5,
    "partnership": 3,
    "upgrade": 3,
    "launch": 3,
    "mainnet": 4,
    "etf": 5,
    "funding": 3,
    "investment": 3,
    "acquisition": 4,
    "security": 4,
    "attack": 5,
    "stolen": 5,
    "shutdown": 5,
    "collapse": 5,
    "record": 3,
}


def importance_score(title, source, news_type):

    text = normalize_text(
        title + " " + source
    )

    score = 3

    for word, value in IMPORTANT_WORDS.items():

        if word in text:
            score += value

    # منابع اجتماعی کمی اهمیت پایین‌تری دارند
    # مگر اینکه خبر واقعاً مهم باشد
    if news_type == "reddit":
        score -= 1

    # سقف 10
    score = min(score, 10)

    # کف 1
    score = max(score, 1)

    return score


# ============================================================
# TRANSLATION
# ============================================================

def translate_to_persian(text):

    try:

        encoded = urllib.parse.quote(text)

        url = (
            "https://translate.googleapis.com/"
            "translate_a/single"
            "?client=gtx"
            "&sl=auto"
            "&tl=fa"
            "&dt=t"
            f"&q={encoded}"
        )

        data = fetch_url(url, timeout=15)

        if not data:
            return text

        result = json.loads(
            data.decode("utf-8")
        )

        translated = ""

        for part in result[0]:

            if part[0]:
                translated += part[0]

        if translated:
            return translated

    except Exception as e:
        print(
            "Translation error:",
            e
        )

    return text


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def is_duplicate(article, recent_articles):

    title = article.get(
        "title",
        ""
    )

    link = article.get(
        "link",
        ""
    )

    # لینک دقیق
    for old in recent_articles:

        if link and link == old.get(
            "link",
            ""
        ):
            return True

        # عنوان خیلی شبیه
        if similarity(
            title,
            old.get("title", "")
        ) >= 0.88:
            return True

    return False


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": "false"
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

    except Exception as e:

        print(
            "Telegram error:",
            e
        )

        return None


# ============================================================
# MESSAGE
# ============================================================

def build_message(
    symbol,
    article
):

    original_title = html.unescape(
        article["title"]
    ).strip()

    persian_title = translate_to_persian(
        original_title
    )

    source = (
        article.get("source")
        or "Unknown"
    )

    sentiment = analyze_sentiment(
        original_title
    )

    score = importance_score(
        original_title,
        source,
        article.get("type", "news")
    )

    if score >= 9:
        level = "🚨 بسیار مهم"

    elif score >= 7:
        level = "🔥 مهم"

    elif score >= 4:
        level = "🟡 معمولی"

    else:
        level = "⚪ کم‌اهمیت"

    message = (
        f"📰 {symbol} | {level}\n\n"

        f"🔹 {persian_title}\n\n"

        f"📊 اهمیت: {score}/10\n"
        f"📈 تأثیر احتمالی: {sentiment}\n\n"

        f"🗞 منبع: {source}\n"
        f"🔗 {article['link']}"
    )

    return message


# ============================================================
# COLLECT ALL NEWS
# ============================================================

def collect_news():

    all_articles = []

    # --------------------------------
    # Google News
    # --------------------------------

    for symbol, query in COINS.items():

        print(
            f"Google News -> {symbol}"
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

    # --------------------------------
    # Reddit
    # --------------------------------

    for subreddit in REDDIT_SUBREDDITS:

        print(
            f"Reddit -> r/{subreddit}"
        )

        articles = get_reddit(
            subreddit
        )

        for article in articles:

            title = article.get(
                "title",
                ""
            )

            # پیدا کردن ارز مرتبط
            for symbol, query in COINS.items():

                if article_matches_coin(
                    symbol,
                    query,
                    article
                ):

                    copy_article = dict(
                        article
                    )

                    copy_article[
                        "symbol"
                    ] = symbol

                    all_articles.append(
                        copy_article
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
            + article.get("title", "")
            + "|"
            + article.get("link", "")
        )

        seen.add(
            make_id(unique_text)
        )

    save_seen(seen)

    with open(
        START_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "initialized"
        )

    print(
        "Initialization complete."
    )

    print(
        f"Registered {len(articles)} old articles."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    seen = load_seen()

    first_run = not os.path.exists(
        START_FILE
    )

    if first_run:

        initialize_bot()

        return

    print(
        "Collecting new crypto news..."
    )

    articles = collect_news()

    print(
        f"Collected {len(articles)} articles."
    )

    # --------------------------------
    # حذف اخبار تکراری در همین اجرا
    # --------------------------------

    unique_articles = []

    for article in articles:

        if is_duplicate(
            article,
            unique_articles
        ):
            continue

        unique_articles.append(
            article
        )

    print(
        f"After duplicate filter: "
        f"{len(unique_articles)}"
    )

    # --------------------------------
    # ارسال
    # --------------------------------

    new_count = 0

    for article in unique_articles:

        symbol = article.get(
            "symbol",
            "CRYPTO"
        )

        unique_text = (
            symbol
            + "|"
            + article.get("title", "")
            + "|"
            + article.get("link", "")
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

        # --------------------------------
        # خبرهای خیلی ضعیف را نفرست
        # --------------------------------

        if score <= 2:
            print(
                f"Skipped low importance: "
                f"{symbol}"
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
                f"Sent: {symbol} | "
                f"{article.get('source', '')}"
            )

            new_count += 1

        time.sleep(1)

    save_seen(seen)

    print(
        f"Finished. "
        f"Sent {new_count} new articles."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
