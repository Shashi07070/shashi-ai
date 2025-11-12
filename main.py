from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler

BOT_TOKEN = "7657065191:AAEFB43BvFDJNjkvUkq6aT_BsUF-4c1Q9NQ"  # Replace with your BotFather token

WELCOME_MESSAGE = """👋 Welcome {mention} to **THE FOOTBALL ANALYST** ⚽
The Asli Baap of the Market 🔥
Stay active & enjoy the winning market 💰
"""

def new_member(update: Update, context):
    # This event triggers whenever a new user joins
    for member in update.chat_member.new_chat_members:
        mention = f"[{member.first_name}](tg://user?id={member.id})"
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text=WELCOME_MESSAGE.format(mention=mention),
            parse_mode="Markdown"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
app.run_polling()