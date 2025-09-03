# app.py
import asyncio
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # بهتر است توکن را از محیط بگیرید

web_app = FastAPI(title="Telegram + FastAPI Bot Example")

# تابع ساده برای پاسخ به دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات با موفقیت اجرا شد.")

# Lifespan event برای startup و shutdown
@web_app.on_event("startup")
async def startup_event():
    # ساخت اپلیکیشن تلگرام
    telegram_app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن هندلر
    telegram_app.add_handler(CommandHandler("start", start))
    
    # اجرای اپلیکیشن تلگرام در پس‌زمینه
    asyncio.create_task(telegram_app.run_polling())

@web_app.get("/")
async def root():
    return {"message": "FastAPI + Telegram Bot running!"}
