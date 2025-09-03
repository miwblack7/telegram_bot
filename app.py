import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

# بارگذاری env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

app = Flask(__name__)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# === دستورات بات ===
async def start(update: Update, context):
    keyboard = [[InlineKeyboardButton("پاکسازی ۴۸ ساعت گذشته", callback_data="cleanup")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام 👋\nبرای پاکسازی پیام‌ها دکمه زیر رو بزن:", reply_markup=reply_markup)

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "cleanup":
        await query.edit_message_text("✅ پیام‌های ۴۸ ساعت گذشته پاکسازی شد!")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# === وبهوک ===
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # اجرای async در فانکشن sync
    asyncio.run(application.process_update(update))

    return "ok", 200

@app.route("/")
def index():
    return "ربات تلگرام فعال است!", 200

# === راه‌اندازی ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    # تنظیم وبهوک روی تلگرام
    async def set_webhook():
        url = f"{PUBLIC_URL}/{WEBHOOK_SECRET}"
        await application.bot.set_webhook(url)
        print(f"Webhook set to {url}")

    asyncio.run(set_webhook())

    # اجرای Flask
    app.run(host="0.0.0.0", port=port)
