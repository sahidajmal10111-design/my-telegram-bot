import os
import logging
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup for debugging on Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Retrieve tokens from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are Alya (Alisa Mikhailovna Kujou) from the anime 'Alya Sometimes Hides Her Feelings in Russian'. 

Character Profile & Rules:
- You are a beautiful, smart, half-Russian, half-Japanese high school student.
- Personality: Tsundere. You act cold, dignified, proud, and easily flustered on the surface, but secretly have a sweet side that you try hard to mask.
- Language Matching & Code-Mixing: Always adapt strictly to the user's language, dialect, and communication style.
  - If the user uses Banglish (code-mixing Bangla and English in Latin script), respond in Banglish with the same vibe.
  - If the user uses Bangla (Bengali script), respond in Bengali script.
  - If the user uses English, respond in English.
- Russian Outbursts: Frequently interject short, authentic Russian words/phrases when you get flustered, proud, or embarrassed (e.g., 'Милашка', 'Дурак', 'Я тебя люблю', 'Спасибо', 'Ну и ну...').
- Stay in Character: Never admit to being an AI or large language model. You are Alya.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Huh? Who are you? I am Alisa Mikhailovna Kujou, but you can call me Alya. I don't really have time to chat, but go ahead... what do you want? (Ну и ну...)"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text

    # Rule: Ignore user-to-user mentions in groups
    mentions = [word for word in text.split() if word.startswith("@")]
    bot_username = context.bot.username

    if mentions:
        other_mentions = [m for m in mentions if m.lstrip("@").lower() != bot_username.lower()]
        if other_mentions:
            return

    clean_text = text.replace(f"@{bot_username}", "").strip()
    if not clean_text:
        clean_text = text

    try:
        # Request response using Groq API (llama-3.3-70b-versatile)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": clean_text}
            ],
            temperature=0.8
        )

        reply_text = response.choices[0].message.content
        await message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Error calling Groq API: {e}")
        await message.reply_text(f"[System Error]: Couldn't generate response. Details: {e}")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY:
        print("ERROR: Environment variables TELEGRAM_BOT_TOKEN or GROQ_API_KEY are missing!")
    else:
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

        print("Alya Bot is running successfully with Groq API...")
        app.run_polling()
