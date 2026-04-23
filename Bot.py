import requests
import time
import os
from telegram.ext import Updater, CommandHandler

# -------- ENV --------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = str(os.getenv("CHAT_ID"))
API_KEY = os.getenv("API_KEY")

# -------- الرحلة --------
FROM = "ALG"
TO = "IST"
DEPART_DATE = "2026-05-04"
RETURN_DATE = "2026-05-11"

TARGET_TOTAL = 40000
TARGET_DEPART = 20000
TARGET_RETURN = 20000

RUNNING = False
LAST_ALERT = 0

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "skyscanner-flight-search.p.rapidapi.com"
}

def get_prices():
    url = "https://skyscanner-flight-search.p.rapidapi.com/flights/roundtrip"

    querystring = {
        "fromEntityId": FROM,
        "toEntityId": TO,
        "departDate": DEPART_DATE,
        "returnDate": RETURN_DATE,
        "currency": "DZD"
    }

    try:
        res = requests.get(url, headers=headers, params=querystring)
        data = res.json()

        itinerary = data["itineraries"][0]
        total = int(itinerary["price"]["amount"])

        depart = total // 2
        ret = total // 2

        link = "https://www.skyscanner.net/transport/flights/alg/ist/"

        return depart, ret, total, link

    except:
        return None, None, None, None


def monitor(context):
    global LAST_ALERT

    if not RUNNING:
        return

    depart, ret, total, link = get_prices()

    if total:
        print(f"{depart} | {ret} | {total}")

        now = time.time()

        if ((depart < TARGET_DEPART or ret < TARGET_RETURN or total < TARGET_TOTAL)
            and (now - LAST_ALERT > 3600)):

            msg = f"""
🔥 السعر نزل!

✈️ ALG → IST → ALG

📅 ذهاب: {depart} DA
📅 إياب: {ret} DA
💰 المجموع: {total} DA

🔗 احجز: {link}
"""
            context.bot.send_message(chat_id=CHAT_ID, text=msg)
            LAST_ALERT = now


# -------- أوامر Telegram --------
def start(update, context):
    update.message.reply_text("✅ البوت خدام! استعمل /run لبدء المراقبة")

def run(update, context):
    global RUNNING
    RUNNING = True
    update.message.reply_text("🚀 بدأ مراقبة الأسعار")

def stop(update, context):
    global RUNNING
    RUNNING = False
    update.message.reply_text("⛔ تم إيقاف المراقبة")

def status(update, context):
    update.message.reply_text(f"📊 الحالة: {'شغال' if RUNNING else 'متوقف'}")


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("run", run))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("status", status))

    updater.start_polling()

    # تشغيل الفحص كل 5 دقائق
    updater.job_queue.run_repeating(monitor, interval=300, first=10)

    updater.idle()


if __name__ == "__main__":
    main()
