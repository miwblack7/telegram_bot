import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI
import nest_asyncio
import uvicorn
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app برای Render health check
web_app = FastAPI()

@web_app.get("/")
async def root():
    return {"status": "ok"}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("سلام 👋 من یه ربات ساده هستم. هرچی بفرستی پاک می‌کنم 😅")
    await asyncio.sleep(5)
    try:
        await msg.delete()
        await update.message.delete()
    except:
        pass

# echo handler + auto delete
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        try:
            await msg.delete()
            await update.message.delete()
        except:
            pass

async def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("❌ Env var TELEGRAM_TOKEN تنظیم نشده")

    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    public_url  = os.getenv("PUBLIC_URL")
    if not public_url:
        raise RuntimeError("❌ Env var PUBLIC_URL تنظیم نشده")

    port = int(os.getenv("PORT", "10000"))

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # اجرای وبهوک
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=secret_path,
        webhook_url=f"{public_url}/{secret_path}",
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    uvicorn.run(web_app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
