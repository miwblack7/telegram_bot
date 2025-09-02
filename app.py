import os
import logging
import asyncio
import nest_asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# لاگ‌ها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تاخیر پاک شدن پیام
DELETE_DELAY = 10  

# FastAPI app
fastapi_app = FastAPI()

# گرفتن توکن و URL ها از متغیر محیطی
TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")

if not TOKEN or not PUBLIC_URL:
    raise RuntimeError("⚠️ TELEGRAM_TOKEN و PUBLIC_URL باید ست بشن")

# ساخت ربات
application = Application.builder().token(TOKEN).build()


# ------------------- هندلرها -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("سلام 👋 من ربات پاکسازی هستم. پیام‌ها بعد از چند ثانیه پاک میشن 🚮")
    await asyncio.sleep(DELETE_DELAY)
    try:
        await update.message.delete()
        await msg.delete()
    except Exception as e:
        logger.warning(f"خطا در حذف پیام: {e}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(DELETE_DELAY)
        try:
            await update.message.delete()
            await msg.delete()
        except Exception as e:
            logger.warning(f"خطا در حذف پیام: {e}")


# ------------------- ثبت هندلرها -------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# ------------------- FastAPI routes -------------------

@fastapi_app.on_event("startup")
async def on_startup():
    """وقتی سرور بالا میاد، وبهوک ست کنه"""
    await application.bot.set_webhook(url=f"{PUBLIC_URL}/{WEBHOOK_SECRET}")


@fastapi_app.post(f"/{WEBHOOK_SECRET}")
async def webhook(request: Request):
    """دریافت آپدیت‌های تلگرام و پاس دادن به PTB"""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"ok": True}


# ------------------- اجرای main loop -------------------

if __name__ == "__main__":
    import uvicorn
    nest_asyncio.apply()

    # اجرای PTB توی یک تسک جدا
    loop = asyncio.get_event_loop()
    loop.create_task(application.initialize())
    loop.create_task(application.start())

    # اجرای FastAPI با Uvicorn
    uvicorn.run("app:fastapi_app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
