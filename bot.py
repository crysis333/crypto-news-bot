import os
import json
import hashlib
import time
import html
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

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
    "WINK": "WINkLink crypto WIN"
}

SEEN_FILE = "seen_news.json"
START_FILE = "bot_initialized.txt"


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen)[-2000:], f, ensure_ascii=False)


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
        headers={"User-Agent": "Mozilla/5.0"}
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
        print("RSS error:", e)
        return []


def translate_to_persian(text):
    """
    ترجمه رایگان عنوان خبر به فارسی
    """

    try:
        encoded = urllib.parse.quote(text)

        url = (
            "https://translate.googleapis.com/translate_a/single"
            "?client=gtx"
            "&sl=auto"
            "&tl=fa"
            "&dt=t"
            f"&q={encoded}"
        )

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read().decode("utf-8")

        result = json.loads(data)

        translated = ""

        for part in result[0]:
            if part[0]:
                translated += part[0]

        if translated:
            return translated

    except Exception as e:
        print("Translation error:", e)

    return text


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
        print("Telegram error:", e)
        return None


def build_message(symbol, article):
    original_title = html.unescape(article["title"]).strip()

    # ترجمه عنوان
    persian_title = translate_to_persian(original_title)

    source = article["source"] or "Google News"

    message = (
        f"📰 خبر جدید درباره {symbol}\n\n"
        f"🔹 {persian_title}\n\n"
        f"🗞 منبع: {source}\n\n"
        f"🔗 {article['link']}"
    )

    return message


def main():

    seen = load_seen()

    # -----------------------------
    # اولین اجرای ربات
    # -----------------------------
    # خبرهای موجود را فقط ثبت می‌کنیم
    # و برای جلوگیری از ارسال خبرهای قدیمی
    # هیچ خبری ارسال نمی‌شود.
    # -----------------------------

    first_run = not os.path.exists(START_FILE)

    if first_run:

        print("First run detected.")
        print("Old news will be ignored.")

        for symbol, query in COINS.items():

            print(f"Initializing {symbol}...")

            articles = get_rss(query)

            for article in articles:

                unique_text = (
                    symbol
                    + "|"
                    + article["title"]
                    + "|"
                    + article["link"]
                )

                seen.add(make_id(unique_text))

        save_seen(seen)

        with open(START_FILE, "w", encoding="utf-8") as f:
            f.write("initialized")

        print("Initialization complete.")
        print("No old news was sent.")

        return

    # -----------------------------
    # اجراهای بعدی
    # -----------------------------

    new_count = 0

    for symbol, query in COINS.items():

        print(f"Checking {symbol}...")

        articles = get_rss(query)

        # فقط چند خبر آخر بررسی شود
        for article in reversed(articles[:5]):

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

            seen.add(news_id)

            message = build_message(symbol, article)

            result = send_telegram(message)

            if result:
                print(f"Sent new news: {symbol}")
                new_count += 1

            time.sleep(1)

    save_seen(seen)

    print(f"Finished. Sent {new_count} new articles.")


if __name__ == "__main__":
    main()
