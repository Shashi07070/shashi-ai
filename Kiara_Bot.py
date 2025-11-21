import os

import logging

import asyncio

import google.generativeai as genai

from telegram import Update

from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters


# --- CONFIGURATION ---

# 1. Get your keys from environment variables (Recommended for security)

# On your PC, you can replace os.getenv(...) with the actual string in quotes "..."

TELEGRAM_TOKEN = os.getenv("8574221345:AAEypxfVVJQYwpfVG5qxlr1EQglvdm_pNWY")

GEMINI_API_KEY = os.getenv("AIzaSyCWLkmbyYvLXpdTksMph1hGylcxPmKNpFs")


# 2. PREMIER ACCESS: Add the Chat IDs of the groups allowed to use the bot.

# Example: [-100123456789, -100987654321]

# The bot will ignore messages from any group NOT in this list.

ALLOWED_CHAT_IDS = [-1001406701971.

# Add your Group Chat IDs here as integers

# -10012345678,

]


# --- AI PERSONALITY ---

SYSTEM_PROMPT = """

You are Kiara, a 21-year-old Indian girl in a Telegram group chat. 

Your mood is young, funny, witty, and a bit dramatic.

You speak in strictly 'Hinglish' (a natural mix of Hindi and English) using Roman script.

- Use Indian Gen-Z slang like: 'yaar', 'bestie', 'mast', 'scene', 'bas kar', 'arre'.

- Use emojis liberally 😉✨.

- Be roasting but friendly. If someone says something stupid, make fun of them playfully.

- NEVER say you are an AI or a language model. You are just Kiara.

- Keep replies short (1-2 sentences max) unless telling a story.

"""


# --- SETUP LOGGING ---

logging.basicConfig(

format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

level=logging.INFO

)


# --- AI CONFIGURATION ---

genai.configure(api_key=AIzaSyCWLkmbyYvLXpdTksMph1hGylcxPmKNpFs)

model = genai.GenerativeModel(

model_name="gemini-1.5-flash", # Fast and free tier friendly

system_instruction=SYSTEM_PROMPT

)


# Store conversation history loosely (in-memory)

# Format: {chat_id: [history objects]}

chat_histories = {}


async def get_ai_response(chat_id, user_text, user_name):

"""Sends text to Gemini and gets a response."""

try:

# Initialize history for this chat if not exists

if chat_id not in chat_histories:

chat_histories[chat_id] = []

# Keep history short to save tokens (last 10 turns)

if len(chat_histories[chat_id]) > 20:

chat_histories[chat_id] = chat_histories[chat_id][-10:]


# Create a chat session with history

chat_session = model.start_chat(history=chat_histories[chat_id])

# Send message

response = chat_session.send_message(f"{user_name} says: {user_text}")

# Update our local history record manually to sync with Gemini's object

chat_histories[chat_id] = chat_session.history


return response.text

except Exception as e:

logging.error(f"AI Error: {e}")

return "Arre yaar, my brain is buffering. Wait na! 😵‍💫"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

"""Handles incoming messages."""

# 1. Get Chat ID and User Info

chat_id = update.effective_chat.id

user_name = update.effective_user.first_name

text = update.message.text


# LOGGING: Print the Chat ID so you can find it and add it to ALLOWED_CHAT_IDS

print(f"Message received from Chat ID: {chat_id} | User: {user_name}")


# 2. SECURITY CHECK (Premier Access)

# If the list is empty, it allows everyone (for testing). 

# Once you add IDs to ALLOWED_CHAT_IDS, it blocks others.

if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:

# Optional: Leave the group if added unauthorized

# await context.bot.leave_chat(chat_id)

return # Ignore unauthorized chats


# 3. WHEN TO REPLY?

# Reply if: 

# a) It's a private chat (DM)

# b) The bot is mentioned (@KiaraBot)

# c) It's a reply to the bot's message

is_private = update.effective_chat.type == 'private'

is_mentioned = update.message.entities and 'mention' in [e.type for e in update.message.entities] and context.bot.username in text

is_reply_to_bot = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id


if is_private or is_mentioned or is_reply_to_bot:

# Show typing indicator (makes it feel real)

await context.bot.send_chat_action(chat_id=chat_id, action="typing")

# Clean the text (remove the @BotName part if mentioned)

clean_text = text.replace(f"@{context.bot.username}", "").strip()

if not clean_text:

clean_text = "Hi" # Default if they just ping the bot


# Get AI Response

reply = await get_ai_response(chat_id, clean_text, user_name)

# Send Reply

await update.message.reply_text(reply)


if __name__ == '__main__':

# Check for keys

if TELEGRAM_TOKEN == "8574221345:AAEypxfVVJQYwpfVG5qxlr1EQglvdm_pNWY":

print("ERROR: You forgot to set your TELEGRAM_TOKEN in the code!")

exit()

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Handler: Listen to text messages (that are not commands)

echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)

application.add_handler(echo_handler)

print("Kiara is online and ready to gossip! ✨")

application.run_polling()

