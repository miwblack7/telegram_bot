# app.py
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DELETE_DELAY = 5  # ثانیه قبل از پاک شدن پیام‌ها

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and auto-delete it after DELETE_DELAY seconds."""
    msg = await update.message.reply_text(
        "سلام! 👋 من یک بات پاکسازی هستم.\nپیام‌ها بعد از چند ثانیه پاک می‌شوند 🤖"
    )
    await asyncio.sleep(DELETE_DELAY)
    await msg.delete()
    # پاک کردن پیام /start کاربر هم
    await update.message.delete()

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete both the user message and bot reply after DELETE_DELAY seconds."""
    if update.message and update.message.text:
        # پاسخ ربات
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(DELETE_DELAY)
        # پاک کردن پیام ربات و پیام کاربر
        await msg.delete()
        await update.message.delete()

# --- Main ---

if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    PUBLIC_URL = os.getenv("PUBLIC_URL")
    WEBHOOK_PATH = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    PORT = int(os.getenv("PORT", "8000"))

    if not TOKEN or not PUBLIC_URL:
        raise RuntimeError("Env vars TELEGRAM_TOKEN و PUBLIC_URL باید تنظیم شوند!")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{PUBLIC_URL}/{WEBHOOK_PATH}",
        drop_pending_updates=True,
    )
