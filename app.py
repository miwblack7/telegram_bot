import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
from datetime import datetime, timedelta

# بارگذاری env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

flask_app = Flask(__name__)

# ساخت اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()

# ========== دستورات بات ==========
async def start(update: Update, context):
    keyboard = [[InlineKeyboardButton("پاکسازی ۴۸ ساعت گذشته", callback_data="cleanup")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام 👋\nبرای پاکسازی پیام‌ها دکمه زیر رو بزن:", reply_markup=reply_markup)

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "cleanup":
        chat_id = query.message.chat_id
        until = datetime.now() - timedelta(hours=48)

        # پاکسازی پیام‌ها
        async for msg in application.bot.get_chat_history(chat_id, limit=100):
            if msg.date >= until:
                try:
                    await application.bot.delete_message(chat_id, msg.message_id)
                except:
                    pass

        await query.edit_message_text("✅ پیام‌های ۴۸ ساعت گذشته پاکسازی شد!")

# اضافه کردن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# ========== وبهوک ==========
@flask_app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok", 200

@flask_app.route("/")
def index():
    return "ربات تلگرام فعال است!", 200

# ========== اجرای Flask + وبهوک ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    async def main():
        url = f"{PUBLIC_URL}/{WEBHOOK_SECRET}"
        await application.bot.set_webhook(url)
        print(f"Webhook set to {url}")
        flask_app.run(host="0.0.0.0", port=port)

    asyncio.run(main())
