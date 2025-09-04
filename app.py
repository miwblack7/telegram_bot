import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PUBLIC_URL = os.getenv("PUBLIC_URL")  # مثل https://your-app.onrender.com
if not PUBLIC_URL:
    raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

bot = Bot(token=TOKEN)
app = FastAPI()

application = Application.builder().token(TOKEN).build()

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من یک بات ساده‌ام 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ---- FastAPI Routes ----
@app.post(f"/{WEBHOOK_SECRET}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{PUBLIC_URL}/{WEBHOOK_SECRET}")
    logger.info(f"Webhook set to {PUBLIC_URL}/{WEBHOOK_SECRET}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logger.info("Webhook deleted")

@app.get("/")
async def home():
    return {"message": "Bot is running ✅"}
