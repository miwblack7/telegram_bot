import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# لاگ‌ها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# اپ FastAPI
web_app = FastAPI()
telegram_app: Application | None = None

# ───── هندلرها ─────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("سلام 👋")
    await asyncio.sleep(5)
    try:
        await update.message.delete()
        await msg.delete()
    except Exception as e:
        logger.warning(f"پاک‌کردن پیام شکست خورد: {e}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        try:
            await update.message.delete()
            await msg.delete()
        except Exception as e:
            logger.warning(f"پاک‌کردن پیام شکست خورد: {e}")

# ───── Routes ─────
@web_app.get("/")
async def root():
    return {"status": "ok"}

@web_app.post("/{secret_path}")
async def telegram_webhook(request: Request, secret_path: str):
    global telegram_app
    if secret_path != os.getenv("WEBHOOK_SECRET", "secret"):
        return {"error": "forbidden"}

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

# ───── startup با lifespan (جدید) ─────
@web_app.on_event("startup")
async def startup_event():
    global telegram_app

    TOKEN = os.getenv("TELEGRAM_TOKEN")
    PUBLIC_URL = os.getenv("PUBLIC_URL")
    SECRET_PATH = os.getenv("WEBHOOK_SECRET", "secret")

    if not TOKEN or not PUBLIC_URL:
        raise RuntimeError("⚠️ متغیرهای TELEGRAM_TOKEN و PUBLIC_URL باید ست بشن.")

    telegram_app = Application.builder().token(TOKEN).build()

    # هندلرها
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # ست‌کردن وبهوک
    await telegram_app.bot.set_webhook(f"{PUBLIC_URL}/{SECRET_PATH}")
    logger.info("✅ وبهوک ست شد.")

# ───── اجرا ─────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(web_app, host="0.0.0.0", port=port)
