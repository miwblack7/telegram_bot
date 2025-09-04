import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------
# دستورات ربات
# ---------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام! 👋 من یک بات ساده هستم.\nهرچی بفرستی، همونو برمی‌گردونم 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

# ---------------------
# Flask App
# ---------------------
flask_app = Flask(__name__)

# health check برای UptimeRobot
@flask_app.route("/ping")
def ping():
    return "pong 🏓", 200

async def setup_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    public_url  = os.getenv("PUBLIC_URL")
    if not public_url:
        raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # اتصال webhook
    await app.bot.set_webhook(f"{public_url}/{secret_path}")

    # route برای تلگرام
    @flask_app.post(f"/{secret_path}")
    def webhook():
        update = Update.de_json(request.get_json(force=True), app.bot)
        app.update_queue.put_nowait(update)
        return "ok", 200

    return app

# ---------------------
# اجرای برنامه
# ---------------------
if __name__ == "__main__":
    import asyncio
    application = asyncio.run(setup_bot())
    port = int(os.getenv("PORT", "8000"))
    flask_app.run(host="0.0.0.0", port=port)
