import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
import uvicorn

nest_asyncio.apply()

# ---------- FastAPI Keep-Alive ----------
keep_alive_app = FastAPI()
keep_alive_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@keep_alive_app.get("/")
async def ping():
    return {"status": "alive"}

# ---------- Telegram Bot Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("سلام! 👋 من یک بات پاک‌کن هستم.")
    await asyncio.sleep(5)  # بعد 5 ثانیه پاک کن
    await msg.delete()
    await update.message.delete()

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        await msg.delete()
        await update.message.delete()

# ---------- Main Function ----------
async def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    public_url  = os.getenv("PUBLIC_URL")
    if not public_url:
        raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

    port = int(os.getenv("PORT", "8000"))

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=secret_path,
        webhook_url=f"{public_url}/{secret_path}",
        drop_pending_updates=True,
    )

# ---------- Run Both FastAPI + Telegram ----------
if __name__ == "__main__":
    import threading

    # Run FastAPI keep-alive server
    def run_keep_alive():
        uvicorn.run(keep_alive_app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

    threading.Thread(target=run_keep_alive, daemon=True).start()

    # Run Telegram bot
    asyncio.run(main())
