import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DELETE_DELAY = 5  # ثانیه تا پیام ربات حذف شود

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(
        "سلام! 👋 من یک ربات پاک‌کننده هستم.\nپیام‌های من بعد از چند ثانیه حذف می‌شوند 🤖"
    )
    await asyncio.sleep(DELETE_DELAY)
    await msg.delete()

# echo handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(DELETE_DELAY)
        await msg.delete()

async def main() -> None:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

    PUBLIC_URL = os.getenv("PUBLIC_URL")
    if not PUBLIC_URL:
        raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

    WEBHOOK_PATH = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    PORT = int(os.getenv("PORT", "8000"))

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # فقط این خط، loop را خود PTB مدیریت می‌کند
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{PUBLIC_URL}/{WEBHOOK_PATH}",
        drop_pending_updates=True,
    )

# ⚡️ تغییر اصلی: asyncio.run() حذف شد
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # برای Render / Jupyter محیطی که loop از قبل فعال است
    asyncio.get_event_loop().run_until_complete(main())
