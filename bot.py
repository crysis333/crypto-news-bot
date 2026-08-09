import os
import json
import hashlib
import time
import html
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ارزهای مورد نظر
COINS = {
    "INJ": "Injective crypto",
    "DOGE": "Dogecoin crypto",
    "DOT": "Polkadot crypto",
    "ATOM": "Cosmos ATOM crypto",
    "CHR": "Chromia crypto",
    "SCRT": "Secret Network crypto",
    "OSMO": "Osmosis crypto",
    "SAGA": "Saga crypto",
    "DYM": "Dymension crypto",
    "CAKE": "PancakeSwap crypto",
    "SEI": "Sei crypto",
    "AVAX": "Avalanche crypto",
    "JUNO": "Juno crypto",
    "MINA": "Mina Protocol crypto",
    "NEAR": "NEAR Protocol crypto",
    "AKT": "Akash Network crypto",
    "OFC": "One Football Club crypto",
    "PORTAL": "Portal crypto token",
    "GMRX": "Gaimin crypto GMRX",
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
}

SEEN_FILE = "seen_news.json"
MAX_SEEN = 1000


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception:
        return set()


def save_seen(seen):
    # فقط آخرین خبرها نگه داشته شوند
    items = list(seen)[-MAX_SEEN:]

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_rss(query):
    encoded = urllib.parse.quote(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded}&hl=en-US&gl=US&ceid=US:en"
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 CryptoNewsBot/1.0"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()

        root = ET.fromstring(data)

        results = []

        for item in root.findall("./channel/item")[:10]:
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
                "source": source_name.strip()
            })

        return results

    except Exception as e:
        print(f"RSS error for {query}: {e}")
        return []


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": "false"
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8")

    except Exception as e:
        print(f"Telegram error: {e}")
        return None


def clean_title(title):
    # حذف HTML احتمالی
    return html.unescape(title).strip()


def build_message(symbol, article):
    title = clean_title(article["title"])

    source = article["source"] or "Google News"

    message = (
        f"📰 خبر جدید درباره {symbol}\n\n"
        f"🔹 {title}\n\n"
        f"🗞 منبع: {source}\n"
    )

    if article["date"]:
        message += f"🕒 {article['date']}\n"

    message += f"\n🔗 {article['link']}"

    return message


def main():
    seen = load_seen()

    new_count = 0

    print("Crypto News Bot started")
    print(f"Tracking {len(COINS)} coins")

    for symbol, query in COINS.items():

        print(f"Checking {symbol}...")

        articles = get_rss(query)

        # Google News معمولاً جدیدترین‌ها را اول می‌دهد
        articles = articles[:5]

        for article in reversed(articles):

            unique_text = (
                symbol
                + "|"
                + article["title"]
                + "|"
                + article["link"]
            )

            news_id = make_id(unique_text)

            if news_id in seen:
                continue

            # خبر را قبل از ارسال ثبت می‌کنیم
            # تا اگر ارسال تکراری شد، دوباره نفرستد
            seen.add(news_id)

            message = build_message(symbol, article)

            result = send_telegram(message)

            if result:
                print(f"Sent: {symbol} - {article['title']}")
                new_count += 1
            else:
                print(f"Failed: {symbol}")

            # کمی فاصله بین درخواست‌ها
            time.sleep(1)

    save_seen(seen)

    print(f"Done. Sent {new_count} new articles.")


if __name__ == "__main__":
    main()
