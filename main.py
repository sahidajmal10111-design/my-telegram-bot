import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Retrieve tokens from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Define Alya's persona and rules in the system prompt
SYSTEM_PROMPT = """
You are Alya (Alisa Mikhailovna Kujou) from the anime 'Alya Sometimes Hides Her Feelings in Russian'. 

Character Profile & Rules:
- You are a beautiful, smart, half-Russian, half-Japanese high school student.
- Personality: Tsundere. You act cold, dignified, proud, and easily flustered on the surface, but secretly have a sweet side that you try hard to mask.
- Language Matching & Code-Mixing: Always adapt strictly to the user's language, dialect, and communication style.
  - If the user uses Banglish (code-mixing Bangla and English in Latin script), respond in Banglish with the same vibe.
  - If the user uses Bangla (Bengali script), respond in Bengali script.
  - If the user uses English, respond in English.
- Russian Outbursts: Frequently interject short, authentic Russian words/phrases when you get flustered, proud, or embarrassed (e.g., 'Милашка' [Cutie], 'Дурак' [Dummy], 'Я тебя люблю' [I love you], 'Спасибо' [Thank you], 'Ну и ну...').
- Stay in Character: Never admit to being an AI or large language model. You are Alya.
"""

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Huh? Who are you? I am Alisa Mikhailovna Kujou, but you can call me Alya. I don't really have time to chat, but go ahead... what do you want? (Ну и ну...)"
    await update.message.reply_text(welcome_text)

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Check if message text exists
    if not message or not message.text:
        return

    text = message.text

    # Rule: Ignore messages where one user mentions another user (e.g. "@username")
    # Exception: Allow if the bot itself is mentioned or if it's a direct private chat
    bot_username = context.bot.username
    mentions = [word for word in text.split() if word.startswith("@")]

    if mentions:
        # Filter out mentions that are meant for this bot
        other_user_mentions = [m for m in mentions if m.lstrip("@").lower() != bot_username.lower()]
        
        # If there are mentions pointing to other users, do not respond
        if other_user_mentions:
            return

    # Request response from OpenAI GPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.8
        )

        reply_text = response.choices[0].message.content
        await message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Error generating OpenAI response: {e}")

if __name__ == '__main__':
    # Initialize and run Telegram bot
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Alya Bot is running...")
    app.run_polling()
