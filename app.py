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

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and auto-delete it after 5 seconds."""
    msg = await update.message.reply_text(
        "سلام! 👋 من یک بات ساده هستم.\nپیام‌ها بعد از چند ثانیه پاک می‌شوند 🤖"
    )
    await asyncio.sleep(5)
    await msg.delete()

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message and delete the bot reply after 5 seconds."""
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        await msg.delete()

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

    # PTB خودش loop را مدیریت می‌کند، نیازی به nest_asyncio نیست
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{PUBLIC_URL}/{WEBHOOK_PATH}",
        drop_pending_updates=True,
    )
