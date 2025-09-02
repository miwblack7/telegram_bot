import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(
        "سلام! 👋 من یک بات پاک‌کننده هستم.\nپیام‌ها بعد از چند ثانیه پاک می‌شوند."
    )
    # پاک کردن پیام ربات و کاربر بعد ۵ ثانیه
    await msg.delete(delay=5)
    await update.message.delete(delay=5)

# echo handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        # پاک کردن پیام بعد ۵ ثانیه
        await msg.delete(delay=5)
        await update.message.delete(delay=5)

# گرفتن توکن و URL ها از محیط
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PUBLIC_URL = os.getenv("PUBLIC_URL")
if not PUBLIC_URL:
    raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

PORT = int(os.getenv("PORT", "8000"))

# ساخت اپلیکیشن
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# اجرای Webhook (بدون asyncio.run)
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=WEBHOOK_SECRET,
    webhook_url=f"{PUBLIC_URL}/{WEBHOOK_SECRET}",
    drop_pending_updates=True
)
