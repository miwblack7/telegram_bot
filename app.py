import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DELETE_DELAY = 10  # چند ثانیه بعد پیام‌ها پاک بشن

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("سلام 👋 من ربات پاکسازی هستم.\nهر پیامی بدی چند ثانیه بعد پاک میشه 🚮")
    await asyncio.sleep(DELETE_DELAY)
    try:
        await update.message.delete()
        await msg.delete()
    except Exception as e:
        logger.warning(f"خطا در حذف پیام: {e}")

# echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(DELETE_DELAY)
        try:
            await update.message.delete()
            await msg.delete()
        except Exception as e:
            logger.warning(f"خطا در حذف پیام: {e}")

async def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("⚠️ متغیر محیطی TELEGRAM_TOKEN ست نشده")

    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    public_url = os.getenv("PUBLIC_URL")
    if not public_url:
        raise RuntimeError("⚠️ متغیر محیطی PUBLIC_URL ست نشده")

    port = int(os.getenv("PORT", "8000"))

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=secret_path,
        webhook_url=f"{public_url}/{secret_path}",
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
