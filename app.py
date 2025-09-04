import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from quart import Quart, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ ربات ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام! 👋 من یک بات ساده هستم.\nهرچی بفرستی، همونو برمی‌گردونم 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

# ------------------ سرور / Ping ------------------

app_server = Quart(__name__)

@app_server.route("/ping")
async def ping():
    return jsonify({"status": "ok"}), 200

# ------------------ Main ------------------

async def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    public_url = os.getenv("PUBLIC_URL")
    if not public_url:
        raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

    port = int(os.getenv("PORT", "8000"))

    bot_app = Application.builder().token(token).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # اجرای وبهوک تلگرام
    await bot_app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=secret_path,
        webhook_url=f"{public_url}/{secret_path}",
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    import asyncio

    # اجرای همزمان سرور Quart و ربات تلگرام
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_until_complete(app_server.run_task(host="0.0.0.0", port=int(os.getenv("PORT", 8000))))
