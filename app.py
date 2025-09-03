import os
import logging
import asyncio
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_app: Application | None = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("سلام 👋")
    await asyncio.sleep(5)
    await update.message.delete()
    await msg.delete()

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        await update.message.delete()
        await msg.delete()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    PUBLIC_URL = os.getenv("PUBLIC_URL")
    SECRET_PATH = os.getenv("WEBHOOK_SECRET", "secret")

    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # ست کردن وبهوک
    await telegram_app.bot.set_webhook(f"{PUBLIC_URL}/{SECRET_PATH}")
    logger.info("✅ وبهوک ست شد.")

    yield  # اینجا اپ روشن میشه

    # اینجا وقتی اپ خاموش شد اجرا میشه
    await telegram_app.shutdown()

web_app = FastAPI(lifespan=lifespan)

@web_app.get("/")
async def root():
    return {"status": "ok"}

@web_app.post("/{secret_path}")
async def telegram_webhook(request: Request, secret_path: str):
    if secret_path != os.getenv("WEBHOOK_SECRET", "secret"):
        return {"error": "forbidden"}

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(web_app, host="0.0.0.0", port=port)
