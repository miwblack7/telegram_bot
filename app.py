import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# --- دستورات ربات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("سلام! 👋 من یک بات پاک‌کننده هستم.\nپیام شما بعد ۵ ثانیه پاک می‌شود.")
    # پاک کردن پیام بعد ۵ ثانیه
    await asyncio.sleep(5)
    await msg.delete()
    await update.message.delete()  # پیام کاربر هم پاک می‌شود

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        msg = await update.message.reply_text(update.message.text)
        await asyncio.sleep(5)
        await msg.delete()
        await update.message.delete()  # پیام کاربر هم پاک می‌شود

# --- برنامه اصلی ---
async def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("Env var TELEGRAM_TOKEN تنظیم نشده است.")

    public_url = os.getenv("PUBLIC_URL")
    if not public_url:
        raise RuntimeError("Env var PUBLIC_URL تنظیم نشده است.")

    secret_path = os.getenv("WEBHOOK_SECRET", "super-secret-path")
    port = int(os.getenv("PORT", "8000"))

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # ست کردن webhook دستی (Render خودش Port را مدیریت می‌کند)
    await app.bot.set_webhook(f"{public_url}/{secret_path}")

    # اجرای webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=secret_path,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # حل مشکل event loop در Render
    import asyncio
    asyncio.run(main())
