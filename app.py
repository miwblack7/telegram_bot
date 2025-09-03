import os
import asyncio
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ایجاد اپلیکیشن FastAPI
web_app = FastAPI()

# خواندن توکن تلگرام از متغیر محیطی
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# تابع دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات شما آماده است.")

# Lifespan event برای startup و shutdown
@web_app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    
    # اجرای ربات به صورت همزمان با FastAPI
    asyncio.create_task(telegram_app.initialize())
    asyncio.create_task(telegram_app.start())
    print("Telegram Bot started!")

@web_app.on_event("shutdown")
async def shutdown_event():
    await telegram_app.stop()
    await telegram_app.shutdown()
    print("Telegram Bot stopped!")

# مسیر تست FastAPI
@web_app.get("/")
async def root():
    return {"message": "FastAPI is running!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # خواندن پورت از Render
    uvicorn.run("app:web_app", host="0.0.0.0", port=port)
