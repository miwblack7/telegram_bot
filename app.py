import os
import logging
from quart import Quart, jsonify, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- BOT HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام! 👋 من یک بات ساده هستم.\nهرچی بفرستی، همونو برمی‌گردونم 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

# ----------------- MAIN APP -----------------
app = Quart(__name__)

@app.route("/ping")
async def ping():
    return jsonify({"status": "ok"})

@app.route("/webhook/<secret>", methods=["POST"])
async def webhook(secret):
    expected_secret = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    if secret != expected_secret:
        return jsonify({"error": "unauthorized"}), 403

    data = await request.get_json()
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return jsonify({"status": "ok"})

# ----------------- TELEGRAM SETUP -----------------
token = os.getenv("TELEGRAM_TOKEN")
if not token:
    raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

bot = Bot(token)
application = Application.builder().token(token).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ----------------- RUN WEBHOOK -----------------
async def main():
    public_url = os.getenv("PUBLIC_URL")
    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    port = int(os.getenv("PORT", "8000"))

    # ست کردن وبهوک
    await bot.set_webhook(f"{public_url}/webhook/{secret_path}")

    # اجرای اپ Quart
    await app.run_task(host="0.0.0.0", port=port)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
