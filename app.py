import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ====== تنظیمات ======
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN)

# اپ Flask
app = Flask(__name__)

# اپلیکیشن تلگرام
application = Application.builder().token(TOKEN).build()


# ====== هندلرها ======
async def start(update: Update, context):
    await update.message.reply_text("سلام! ربات فعاله ✅")


async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# ====== Webhook ======
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


async def set_webhook():
    public_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    print(f"Setting webhook to {public_url}")
    await bot.delete_webhook()
    await bot.set_webhook(url=public_url)


# ====== اجرای سرور ======
if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
