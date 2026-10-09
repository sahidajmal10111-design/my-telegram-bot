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
    chat_type = message.chat.type  # 'private', 'group', or 'supergroup'

    # Rule: Ignore user-to-user mentions in groups
    # Look for any word starting with '@'
    mentions = [word for word in text.split() if word.startswith("@")]
    bot_username = context.bot.username

    if mentions:
        # Check if another user (not this bot) is mentioned
        other_mentions = [m for m in mentions if m.lstrip("@").lower() != bot_username.lower()]
        if other_mentions:
            return  # Ignore if user mentioned someone else

    # In group chats, optional: clean up the bot's tag from text if tagged
    clean_text = text.replace(f"@{bot_username}", "").strip()
    if not clean_text:
        clean_text = text

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": clean_text}
            ],
            temperature=0.8
        )

        reply_text = response.choices[0].message.content
        await message.reply_text(reply_text)

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    # Handles all text messages in private chats and groups
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Alya Bot is running...")
    app.run_polling()
