import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# لاگ‌گیری
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# متغیرهای محیطی
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("⚠️ متغیر TELEGRAM_TOKEN تنظیم نشده.")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PUBLIC_URL = os.getenv("PUBLIC_URL")
if not PUBLIC_URL:
    raise RuntimeError("⚠️ متغیر PUBLIC_URL تنظیم نشده.")

PORT = int(os.getenv("PORT", "10000"))

# اپ FastAPI
server = FastAPI()

# ساخت بات
application = Application.builder().token(TOKEN).build()

# زمان حذف پیام‌ها (ثانیه)
DELETE_DELAY = 10

async def delete_after_delay(message: Message, delay: int):
    """حذف پیام بعد از چند ثانیه"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.warning(f"❌ خطا در حذف پیام: {e}")

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        sent = await update.message.reply_text("سلام 👋 من روی Render ران شدم!\nپیام‌ها بعد چند ثانیه پاک میشن 🧹")
        # حذف پیام کاربر و جواب بات
        asyncio.create_task(delete_after_delay(update.message, DELETE_DELAY))
        asyncio.create_task(delete_after_delay(sent, DELETE_DELAY))

# هندل پیام عادی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        sent = await update.message.reply_text(update.message.text)
        # حذف پیام کاربر و جواب بات
        asyncio.create_task(delete_after_delay(update.message, DELETE_DELAY))
        asyncio.create_task(delete_after_delay(sent, DELETE_DELAY))

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# تنظیم وبهوک در استارت سرور
@server.on_event("startup")
async def startup_event():
    logger.info("🚀 Setting webhook...")
    await application.bot.set_webhook(url=f"{PUBLIC_URL}/{WEBHOOK_SECRET}")

# روت وبهوک
@server.post(f"/{WEBHOOK_SECRET}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}
