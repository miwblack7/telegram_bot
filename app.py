import os
import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# فقط برای اجرا‌ی لوکال
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret123")

if not TOKEN or not PUBLIC_URL:
    raise RuntimeError("متغیرهای محیطی TELEGRAM_TOKEN و PUBLIC_URL باید تنظیم شوند.")

app = Flask(__name__)

# نکته کلیدی: بدون Updater تا خطای قبلی ایجاد نشه
application = Application.builder().token(TOKEN).updater(None).build()

# ======= هندلرها =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("پاکسازی ۴۸ ساعت اخیر", callback_data="cleanup")]]
    await update.message.reply_text("سلام 👋 یکی از گزینه‌ها رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(kb))

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "cleanup":
        await q.edit_message_text("در نسخهٔ سرور فقط webhook فعال است. پاکسازی را بعداً اضافه می‌کنیم ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(btn))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ======= راه‌اندازی PTB و تنظیم webhook در استارتاپ =======
async def init_and_set_webhook():
    """Initialize PTB once and set the webhook URL."""
    await application.initialize()
    webhook_url = f"{PUBLIC_URL.rstrip('/')}/{WEBHOOK_SECRET}"
    await application.bot.set_webhook(webhook_url, drop_pending_updates=True)

# در زمان import ماژول، یک‌بار مقداردهی انجام می‌شود
asyncio.run(init_and_set_webhook())

# ======= مسیرهای وب =======
@app.get("/")
def health():
    return {"status": "ok", "webhook": f"/{WEBHOOK_SECRET}"}

# Endpoint دریافت آپدیت‌ها از تلگرام
@app.post(f"/{WEBHOOK_SECRET}")
async def telegram_webhook():
    data = request.get_json(force=True, silent=False)
    update = Update.de_json(data, application.bot)
    # اینجا نیازی به start کردن اپ نیست؛ پردازش مستقیم کافیه
    await application.process_update(update)
    return "ok", 200

# گزینهٔ دستی برای ست وبهوک (اگر لازم شد مجبوراً دوباره ست کنید)
@app.get("/setwebhook")
def set_webhook_manual():
    async def _set():
        await application.bot.set_webhook(f"{PUBLIC_URL.rstrip('/')}/{WEBHOOK_SECRET}", drop_pending_updates=True)
    asyncio.run(_set())
    return jsonify({"ok": True, "webhook": f"{PUBLIC_URL.rstrip('/')}/{WEBHOOK_SECRET}"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
