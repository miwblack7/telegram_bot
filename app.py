import os
import time
from flask import Flask, request
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# دریافت متغیرهای محیطی
TOKEN = os.environ['TELEGRAM_TOKEN']
PUBLIC_URL = os.environ['PUBLIC_URL']
WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# ذخیره پیام‌ها {chat_id: [(message_id, timestamp)]}
messages = {}

# پاکسازی پیام‌های بالای 48 ساعت
def cleanup_messages():
    now = time.time()
    for chat_id in list(messages.keys()):
        messages[chat_id] = [(mid, ts) for mid, ts in messages[chat_id] if now - ts < 48*3600]
        if not messages[chat_id]:
            del messages[chat_id]

# ارسال دکمه شیشه‌ای
def send_cleanup_button(update, context=None):
    keyboard = [[InlineKeyboardButton("پاکسازی همه", callback_data="cleanup_all")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("پاکسازی پیام‌ها:", reply_markup=reply_markup)

# فرمان /start
def start(update, context):
    update.message.reply_text("سلام! من بات پاکسازی هستم.")
    # ذخیره پیام
    chat_id = update.message.chat_id
    messages.setdefault(chat_id, []).append((update.message.message_id, time.time()))
    send_cleanup_button(update)

# کلیک روی دکمه شیشه‌ای
def button(update: Update, context):
    query = update.callback_query
    if query.data == "cleanup_all":
        chat_id = query.message.chat_id
        if chat_id in messages:
            for mid, _ in messages[chat_id]:
                try:
                    bot.delete_message(chat_id=chat_id, message_id=mid)
                except:
                    pass
            del messages[chat_id]
        query.answer("تمام پیام‌ها پاک شدند!")

# ذخیره پیام‌های ورودی
def handle_message(update, context):
    chat_id = update.message.chat_id
    messages.setdefault(chat_id, []).append((update.message.message_id, time.time()))

# تنظیمات Dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dispatcher.add_handler(CallbackQueryHandler(button))

# مسیر وب‌هوک
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    cleanup_messages()
    return "OK"

if __name__ == "__main__":
    # ست کردن وب‌هوک روی تلگرام
    bot.set_webhook(url=f"{PUBLIC_URL}/{WEBHOOK_SECRET}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
