import os
import logging
from fastapi import FastAPI, Request, HTTPException, Header
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---- تنظیمات محیط ----
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
PUBLIC_URL = os.getenv("PUBLIC_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- ساخت اپلیکیشن FastAPI ----
app = FastAPI()

# ---- ساخت ربات ----
bot_app = Application.builder().token(TOKEN).build()

# دستور ساده /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 ربات آماده‌ست!")

bot_app.add_handler(CommandHandler("start", start))


# ---- رویداد lifespan (جایگزین startup/shutdown) ----
@app.on_event("lifespan")
async def lifespan(app: FastAPI):
    logger.info("🔹 Bot starting...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.bot.set_webhook(
        url=f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}"
    )
    yield
    logger.info("🔹 Bot shutting down...")
    await bot_app.stop()
    await bot_app.shutdown()


# ---- مسیر تست ----
@app.get("/")
async def root():
    return {"status": "ok", "message": "Bot is live 🎉"}


# ---- وبهوک ----
@app.post("/webhook/{token}")
async def webhook(request: Request, token: str, x_telegram_bot_api_secret_token: str = Header(None)):
    if token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid token")
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}
