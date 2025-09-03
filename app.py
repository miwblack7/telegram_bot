import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# =======================
# متغیرهای محیطی
# =======================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PUBLIC_URL = os.environ.get("PUBLIC_URL")  # آدرس webhook شما
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

app = Flask(__name__)

# =======================
# دستورات بات
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("پاکسازی 48 ساعت گذشته", callback_data="clear_48h")],
        [InlineKeyboardButton("پاکسازی همه پیام‌ها", callback_data="clear_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "clear_48h":
        await query.edit_message_text(text="در حال پاکسازی پیام‌های ۴۸ ساعت گذشته…")
        # اینجا می‌توانید منطق پاکسازی پیام‌ها را اضافه کنید
    elif query.data == "clear_all":
        await query.edit_message_text(text="در حال پاکسازی همه پیام‌ها…")
        # اینجا هم منطق پاکسازی همه پیام‌ها

# =======================
# وب‌هوک تلگرام
# =======================
@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"

# =======================
# راه‌اندازی بات
# =======================
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# ست کردن webhook روی Render
async def on_startup():
    webhook_url = f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET}"
    await application.bot.set_webhook(webhook_url)

application.post_init = on_startup

# =======================
# اجرای سرور Flask
# =======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
