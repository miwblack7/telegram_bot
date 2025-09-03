import os
import logging
from fastapi import FastAPI, Request, Header, HTTPException
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === ENV ===
TOKEN = os.getenv("TELEGRAM_TOKEN", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is missing")
if not PUBLIC_URL:
    raise RuntimeError("PUBLIC_URL is missing")

# === Logging ===
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot")

# === FastAPI ===
app = FastAPI(title="Telegram Webhook")

# === PTB v21 (بدون Updater) ===
application = Application.builder().token(TOKEN).build()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ✅ ربات وصل شد. /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هرچی بنویسی همونو برمی‌گردونم. برای تست آماده‌ام 🙂")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Lifecycle ---
@app.on_event("startup")
async def on_startup():
    # init app
    await application.initialize()
    # ست کردن وبهوک (با Secret Header و پاک کردن آپدیت‌های صف)
    webhook_url = f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}"
    try:
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        log.info(f"Webhook set -> {webhook_url}")
    except Exception as e:
        log.exception("Failed to set webhook")
        # ادامه می‌دهیم تا سرویس بالا بماند

@app.on_event("shutdown")
async def on_shutdown():
    try:
        await application.bot.delete_webhook()
    except Exception:
        pass
    await application.shutdown()
    await application.stop()

# --- Health ---
@app.get("/")
async def root():
    return {"ok": True, "msg": "running"}

# --- Webhook endpoint ---
@app.post("/webhook/{secret}")
async def telegram_webhook(
    secret: str,
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    # بررسی secret در مسیر و هدر امنیتی
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="invalid path secret")
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="invalid header secret")

    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}
