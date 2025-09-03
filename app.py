import os
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# تنظیمات محیطی
PUBLIC_URL = os.environ.get("PUBLIC_URL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "secret123")

# ایجاد اپ Flask
app = Flask(__name__)

# ایجاد بات
bot = Bot(token=TELEGRAM_TOKEN)

# ذخیره موقت پیام‌ها برای پاکسازی 48 ساعت
MESSAGES = []

# ----------------------
# مسیر تست سرور
@app.route("/")
def index():
    return "Bot is running!"

# ----------------------
# webhook تلگرام
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    handle_update(update)
    return "OK", 200

# ----------------------
# دستورات بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💡 گزینه اول", callback_data="opt1")],
        [InlineKeyboardButton("✨ گزینه دوم", callback_data="opt2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text("سلام! یک گزینه انتخاب کن:", reply_markup=reply_markup)
    
    # ذخیره پیام برای پاکسازی
    MESSAGES.append({"chat_id": update.effective_chat.id, "message_id": msg.message_id, "date": datetime.utcnow()})

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"شما {query.data} را انتخاب کردید.")

# ----------------------
# پاکسازی پیام‌های قدیمی (48 ساعت)
def cleanup_messages():
    global MESSAGES
    now = datetime.utcnow()
    to_delete = [m for m in MESSAGES if now - m["date"] > timedelta(hours=48)]
    for m in to_delete:
        try:
            bot.delete_message(chat_id=m["chat_id"], message_id=m["message_id"])
        except TelegramError:
            pass
    MESSAGES = [m for m in MESSAGES if now - m["date"] <= timedelta(hours=48)]

# ----------------------
# تابع اصلی مدیریت آپدیت
def handle_update(update: Update):
    from telegram.ext import CallbackContext
    from asyncio import run
    # اجرای دستور start
    if update.message and update.message.text == "/start":
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        run(start(update, CallbackContext(app)))
    elif update.callback_query:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        run(button(update, CallbackContext(app)))
    
    # پاکسازی پیام‌های قدیمی
    cleanup_messages()

# ----------------------
# تنظیم webhook
@app.route("/set_webhook")
def set_webhook():
    url = f"{PUBLIC_URL}/{WEBHOOK_SECRET}"
    bot.delete_webhook()
    s = bot.set_webhook(url)
    return f"Webhook set: {s}"

# ----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
