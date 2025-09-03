import os
import asyncio
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# ENV vars
TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")

# Flask app
app = Flask(__name__)

# --- Telegram Application ---
# updater=False باعث میشه اصلا Updater ساخته نشه
application = Application.builder().token(TOKEN).updater(None).build()

# --- Handlers ---
async def start(update: Update, context):
    await update.message.reply_text("✅ ربات به وبهوک وصل شد و درست کار می‌کنه!")

application.add_handler(CommandHandler("start", start))

# --- Flask Routes ---
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "ok", 200
    else:
        abort(405)

@app.route("/", methods=["GET"])
def home():
    return "ربات فعال است ✅"

# --- Run ---
if __name__ == "__main__":
    bot = Bot(TOKEN)
    url = f"{PUBLIC_URL}/{WEBHOOK_SECRET}"

    async def set_webhook():
        await bot.delete_webhook()
        await bot.set_webhook(url)

    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=10000)
