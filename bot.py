from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("group_manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# خوشامدگویی به کاربر جدید
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for user in message.new_chat_members:
        await message.reply_text(f"👋 خوش اومدی {user.mention} به گروه!")

# دستور بن
@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message):
    if not message.reply_to_message:
        return await message.reply("⚠️ باید روی پیام کاربر ریپلای کنی.")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.kick_chat_member(message.chat.id, user_id)
        await message.reply("🚫 کاربر بن شد.")
    except:
        await message.reply("❌ نتونستم بن کنم. مطمئن شو من ادمینم.")

# دستور حذف پیام
@app.on_message(filters.command("del") & filters.group)
async def delete_message(client, message):
    if message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()
    else:
        await message.reply("⚠️ باید روی پیام ریپلای کنی تا حذف بشه.")

print("🤖 Bot is running...")
app.run()
