import os
import asyncio
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
app = FastAPI()
telegram_app = None  # متغیر سراسری برای ربات

# هندلر ساده دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات شما آماده است.")

# Lifespan Events استاندارد
@app.on_event("startup")
async def startup_event():
    global telegram_app
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    
    # اجرای ربات بصورت همزمان با FastAPI
    asyncio.create_task(telegram_app.initialize())
    asyncio.create_task(telegram_app.start())
    print("Telegram Bot started!")

@app.on_event("shutdown")
async def shutdown_event():
    if telegram_app:
        await telegram_app.stop()
        await telegram_app.shutdown()
        print("Telegram Bot stopped!")

# مسیر تست FastAPI
@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # استفاده از پورت Render
    uvicorn.run("app:app", host="0.0.0.0", port=port)
