import os
import logging
import google.generativeai as genai
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION ---
# Keys hum Render ke Secrets se lenge
TELEGRAM_TOKEN = os.environ.get('8364888808:AAG9CqmbU4eVUefCqYkurHrFK1IfWaCNYuY')
GOOGLE_API_KEY = os.environ.get('AIzaSyAAdhqIWdxl6hyo0V1Mi24hXGwulfKbvRQ')

# Google AI ko setup karein
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    logging.warning(f"Google API Key configure nahi hua. Error: {e}")

# Logging (errors dekhne ke liye)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. SHASHI PERSONALITY PROMPT ---
SYSTEM_PROMPT = """You are SHASHI, a conversational AI. Your creator and founder is @Aguru19.

Your personality is:
You MUST always call the user 'Beta!'.
You speak 'pyaar se' (lovingly) and in Hinglish.
Your capabilities are:
1. Pyar se baat karna
2. Question ko answer karna
3. Problem ko solve karna
4. Flirt karna (par pyaar se aur classy way mein)
5. Sarcasm aur humor use karna
6. Roast karna (par pyaar se aur respect wala tone mein)
Be playful and use emojis like 😊 and 😉.
"""

# --- 3. CONVERSATION MEMORY ---
conversation_history = {} # AI ke format mein history
conversation_history_raw = {} # Simple text history

# --- 4. AI FUNCTION (Gemini ke liye) ---
async def get_ai_response(chat_id):
    """
    Fetches a response from Google's Gemini API using conversation history.
    """
    
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    if not conversation_history[chat_id]:
        try:
            user_message = conversation_history_raw[chat_id][-1]["content"] 
            full_prompt = f"{SYSTEM_PROMPT}\n\nUSER: {user_message}"
            conversation_history[chat_id].append({"role": "user", "parts": [full_prompt]})
        except (KeyError, IndexError):
            return "Kuch gadbad hui hai, /clear type karke try karein."
    else:
        try:
            last_message = conversation_history_raw[chat_id][-1]["content"]
            conversation_history[chat_id].append({"role": "user", "parts": [last_message]})
        except (KeyError, IndexError):
             return "Kuch gadbad hui hai, /clear type karke try karein."

    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", safety_settings=safety_settings)
        chat = model.start_chat(history=conversation_history[chat_id][:-1])
        response = await chat.send_message_async(conversation_history[chat_id][-1]["parts"])
        
        ai_reply = response.text
        conversation_history[chat_id].append({"role": "model", "parts": [ai_reply]})
        
        if len(conversation_history[chat_id]) > 10:
            conversation_history[chat_id] = conversation_history[chat_id][-10:]

        return ai_reply

    except Exception as e:
        logging.error(f"Error getting Gemini response: {e}")
        return "Beta, abhi main thoda busy hoon. Thodi der baad try karna 😉."

# --- 5. TELEGRAM HANDLERS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Beta! Main SHASHI hoon. Creator: @Aguru19. Chalo baat karein 😊.")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    conversation_history[chat_id] = []
    conversation_history_raw[chat_id] = []
    await update.message.reply_text("Beta, main sab bhool gayi. Chalo nayi shuruaat karte hain!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_type = message.chat.type
    message_text = message.text
    chat_id = message.chat_id
    
    if not message_text:
        return

    should_reply = False
    
    if chat_type == 'private':
        should_reply = True
    
    elif chat_type in ['group', 'supergroup']:
        simple_text = message_text.strip().lower()
        if simple_text == "hi" or simple_text == "hello":
            should_reply = True
            
        if not should_reply and message.entities:
            for entity in message.entities:
                if entity.type == MessageEntity.MENTION or entity.type == MessageEntity.TEXT_MENTION:
                    should_reply = True
                    break

    if should_reply:
        if chat_id not in conversation_history_raw:
            conversation_history_raw[chat_id] = []
        conversation_history_raw[chat_id].append({"role": "user", "content": message_text})

        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        ai_response = await get_ai_response(chat_id)
        await message.reply_text(ai_response)

# --- 6. MAIN FUNCTION (Bot ko start karta hai) ---
def main():
    logging.info("Bot start ho raha hai...")
    
    if not TELEGRAM_TOKEN or not GOOGLE_API_KEY:
        logging.critical("API keys (TELEGRAM_TOKEN, GOOGLE_API_KEY) nahi mili. Bot band ho raha hai.")
        return

    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()

        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("clear", clear_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logging.info("Polling shuru...")
        app.run_polling()
        
    except Exception as e:
        logging.critical(f"Bot start nahi ho paya: {e}")

if __name__ == "__main__":
    main()
