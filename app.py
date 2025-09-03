import os
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# بارگذاری .env (فقط در لوکال)
load_dotenv()

# متغیرهای محیطی
TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret123")

# ساخت اپلیکیشن Flask
app = Flask(__name__)

# ساخت بات
application = Application.builder().token(TOKEN).build()

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("پاکسازی پیام‌ها (۴۸ ساعت اخیر)", callback_data="cleanup")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام 👋 یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)

# ثبت هندلر
application.add_handler(CommandHandler("start", start))

# روت برای webhook
@app.post(f"/{WEBHOOK_SECRET}")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok", 200

# health check برای Render
@app.get("/")
def index():
    return {"status": "ok", "message": "Bot is running!"}

# ست کردن webhook هنگام شروع
@app.before_request
def before_first_request():
    # این فانکشن فقط بار اول اجرا میشه
    webhook_url = f"{PUBLIC_URL}/{WEBHOOK_SECRET}"
    app.logger.info(f"Setting webhook to: {webhook_url}")
    application.bot.set_webhook(url=webhook_url)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
