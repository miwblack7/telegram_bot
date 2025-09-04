import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- Config ----------------
TOKEN = os.getenv("BOT_TOKEN", "8344618608:AAEZzCZ3I96lp_Xipm7c03TJrwLRiZlQAG4")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "hhhh55")
APP_URL = os.getenv("APP_URL", "https://telegram-bot-mocw.onrender.com")

logging.basicConfig(level=logging.INFO)

app = FastAPI()
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# ---------------- Handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 🌹 ربات با موفقیت کار می‌کنه.")

application.add_handler(CommandHandler("start", start))

# ---------------- FastAPI Routes ----------------
@app.post(f"/webhook/{WEBHOOK_SECRET}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def home():
    return {"message": "Bot is running ✅"}

# ---------------- Startup & Shutdown ----------------
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{APP_URL}/webhook/{WEBHOOK_SECRET}")
    logging.info(f"✅ Webhook set: {APP_URL}/webhook/{WEBHOOK_SECRET}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logging.info("❌ Webhook removed")
