# app.py
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # اجرای کد هنگام startup
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("سلام! ربات اجرا شد.")))
    
    # اجرای تلگرام در پس‌زمینه
    task = asyncio.create_task(telegram_app.run_polling())
    
    yield  # اینجا اپلیکیشن FastAPI بالا می‌آید
    
    # shutdown: توقف ربات هنگام خاموشی
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

web_app = FastAPI(title="Telegram + FastAPI Bot Example", lifespan=lifespan)

@web_app.get("/")
async def root():
    return {"message": "FastAPI + Telegram Bot running!"}
