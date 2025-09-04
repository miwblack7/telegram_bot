import os
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import threading

# -------------------------
# تنظیمات ربات
# -------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")
PUBLIC_URL = os.getenv("PUBLIC_URL")
if not PUBLIC_URL:
    raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

PORT = int(os.getenv("PORT", 8000))

# -------------------------
# Flask App
# -------------------------
app = Flask(__name__)

# -------------------------
# Handlers تلگرام
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 من یک بات ساده هستم. هرچی بفرستی، همونو برمی‌گردونم 🤖")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

# -------------------------
# ایجاد Application
# -------------------------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# -------------------------
# وبهوک Flask
# -------------------------
@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    """مسیر وبهوک تلگرام"""
    update = Update.de_json(request.get_json(force=True), Bot(TOKEN))
    asyncio.run(application.update_queue.put(update))  # قرار دادن آپدیت در صف
    return "OK", 200

@app.route("/ping", methods=["GET"])
def ping():
    """مسیر Ping برای UptimeRobot"""
    return jsonify({"status": "alive"}), 200

# -------------------------
# اجرای ربات در یک Thread جداگانه
# -------------------------
def run_asyncio_loop():
    asyncio.run(application.initialize())
    asyncio.run(application.start())
    asyncio.run(application.idle())

if __name__ == "__main__":
    # اجرای async loop در thread جدا
    threading.Thread(target=run_asyncio_loop, daemon=True).start()
    # اجرای Flask
    app.run(host="0.0.0.0", port=PORT)
