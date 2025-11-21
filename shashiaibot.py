import os
import logging
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask

# ==========================================
# 👇 THIS IS THE PART YOU ASKED ABOUT 👇
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Kiara is Alive! ✨"

def run_web_server():
    # Render automatically provides a PORT. We must listen on it.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def start_keep_alive():
    # We run the web server in a separate thread so it doesn't block the bot
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()
# ==========================================
# 👆 END OF PATCH 👆
# ==========================================

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("8574221345:AAEypxfVVJQYwpfVG5qxlr1EQglvdm_pNWY")
GEMINI_API_KEY = os.getenv("AIzaSyCWLkmbyYvLXpdTksMph1hGylcxPmKNpFs")
ALLOWED_CHAT_IDS = [-1001406701971] # Your Group ID

# --- AI PERSONALITY ---
SYSTEM_PROMPT = """
You are Kiara, a 21-year-old Indian girl in a Telegram group chat. 
Your mood is young, funny, witty, and a bit dramatic.
You speak in strictly 'Hinglish' (a natural mix of Hindi and English) using Roman script.
- Use Indian Gen-Z slang like: 'yaar', 'bestie', 'mast', 'scene', 'bas kar', 'arre', 'chup kar'.
- Use emojis liberally 😉✨.
- Be roasting but friendly.
- NEVER say you are an AI.
"""

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- AI SETUP ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

chat_histories = {}

async def get_ai_response(chat_id, user_text, user_name):
    if not GEMINI_API_KEY: return "Key missing!"
    try:
        if chat_id not in chat_histories: chat_histories[chat_id] = []
        if len(chat_histories[chat_id]) > 30: chat_histories[chat_id] = chat_histories[chat_id][-15:]
        
        chat_session = model.start_chat(history=chat_histories[chat_id])
        response = chat_session.send_message(f"{user_name}: {user_text}")
        chat_histories[chat_id] = chat_session.history
        return response.text
    except Exception as e:
        logging.error(f"AI Error: {e}")
        return "Arre yaar, network issue. 😵‍💫"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    chat_id = update.effective_chat.id
    if chat_id not in ALLOWED_CHAT_IDS: return

    text = update.message.text
    is_mentioned = context.bot.username in text
    is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id

    if is_mentioned or is_reply:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        clean_text = text.replace(f"@{context.bot.username}", "").strip() or "Bol?"
        reply = await get_ai_response(chat_id, clean_text, update.effective_user.first_name)
        await update.message.reply_text(reply)

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN missing.")
    else:
        # 1. Start the Keep-Alive Server (Important for Render)
        start_keep_alive()
        
        # 2. Start the Bot
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print(f"Kiara is Online! Monitoring: {ALLOWED_CHAT_IDS}")
        application.run_polling()
