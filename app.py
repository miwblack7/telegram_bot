import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# اپ FastAPI
web_app = FastAPI()

# متغیر سراسری برای اپلیکیشن تلگرام
telegram_app: Application = None

# ─────────── هندلرها ───────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("سلام! 👋\nهرچی بفرستی، همونو برمی‌گردونم 🤖")
    await asyncio.sleep(5)  # بعد از ۵ ثانیه پاک کن
    try:
        await update.message.delete()
        await msg.delete()
    except Exception as e:
        logger.warning(f"خطا در پاک‌کردن پیام: {e}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        try:
            await update.message.delete()
            await msg.delete()
        except Exception as e:
            logger.warning(f"خطا در پاک‌کردن پیام: {e}")

# ─────────── FastAPI routes ───────────
@web_app.get("/")
async def root():
    """برای UptimeRobot"""
    return {"status": "ok"}

@web_app.post("/{secret_path}")
async def telegram_webhook(request: Request, secret_path: str):
    """مسیر وب‌هوک تلگرام"""
    if secret_path != os.getenv("WEBHOOK_SECRET", "secret"):
        return {"error": "forbidden"}

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"status": "ok"}

# ─────────── main ───────────
async def main():
    global telegram_app

    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise RuntimeError("⚠️ متغیر محیطی TELEGRAM_TOKEN تنظیم نشده.")

    PUBLIC_URL = os.getenv("PUBLIC_URL")
    if not PUBLIC_URL:
        raise RuntimeError("⚠️ متغیر محیطی PUBLIC_URL تنظیم نشده.")

    SECRET_PATH = os.getenv("WEBHOOK_SECRET", "secret")

    telegram_app = Application.builder().token(TOKEN).build()

    # هندلرها
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # ست‌کردن وب‌هوک
    await telegram_app.bot.set_webhook(f"{PUBLIC_URL}/{SECRET_PATH}")

# ─────────── اجرا ───────────
if __name__ == "__main__":
    import uvicorn

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(web_app, host="0.0.0.0", port=port)
