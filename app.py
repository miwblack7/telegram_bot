import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # لینک وبهوک Render

app = Flask(__name__)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من بات تلگرام شما هستم.")

# ساخت اپلیکیشن تلگرام
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# مسیر وبهوک
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "بات فعال است!"

# ست کردن وبهوک روی Render (یک بار کافی است)
if __name__ == "__main__":
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook"
    r = requests.get(url)
    print(r.text)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
