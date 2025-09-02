import os
import logging
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# فعال کردن لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیمات محیطی
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("⚠️ متغیر محیطی TELEGRAM_TOKEN تنظیم نشده.")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PUBLIC_URL = os.getenv("PUBLIC_URL")
if not PUBLIC_URL:
    raise RuntimeError("⚠️ متغیر محیطی PUBLIC_URL تنظیم نشده.")

PORT = int(os.getenv("PORT", "10000"))

# ساخت اپلیکیشن FastAPI
server = FastAPI()

# ساخت بات
application = Application.builder().token(TOKEN).build()

# هندلر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("سلام! 🌐 من روی Render ران شدم ✅")

application.add_handler(CommandHandler("start", start))

# ست کردن وبهوک روی مسیر خاص
@server.on_event("startup")
async def startup_event():
    logger.info("🚀 Setting webhook...")
    await application.bot.set_webhook(url=f"{PUBLIC_URL}/{WEBHOOK_SECRET}")

# هندل دریافت آپدیت‌ها از تلگرام
@server.post(f"/{WEBHOOK_SECRET}")
async def webhook(req: dict):
    update = Update.de_json(req, application.bot)
    await application.process_update(update)
    return {"ok": True}
