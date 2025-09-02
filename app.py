import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DELETE_DELAY = 5  # ثانیه‌ها قبل از حذف پیام

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(
        "سلام! 👋 من یک بات پاک‌کننده هستم.\nهرچی بفرستی، همونو پاک می‌کنم 🤖"
    )
    # حذف پیام کاربر و پیام ربات بعد از DELETE_DELAY ثانیه
    await asyncio.sleep(DELETE_DELAY)
    try:
        await update.message.delete()
        await msg.delete()
    except Exception as e:
        logger.warning(f"خطا در حذف پیام: {e}")

# echo handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(DELETE_DELAY)
        try:
            await update.message.delete()
            await msg.delete()
        except Exception as e:
            logger.warning(f"خطا در حذف پیام: {e}")

# دریافت تنظیمات از محیط
TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PORT = int(os.getenv("PORT", "8000"))

if not TOKEN or not PUBLIC_URL:
    raise RuntimeError("Env vars TELEGRAM_TOKEN و PUBLIC_URL تنظیم نشده‌اند.")

# ساخت اپلیکیشن
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# اجرای webhook بدون asyncio.run()
if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_SECRET,
        webhook_url=f"{PUBLIC_URL}/{WEBHOOK_SECRET}",
        drop_pending_updates=True,
    )
