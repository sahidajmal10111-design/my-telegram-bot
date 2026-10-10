import os
import asyncio
import logging
from collections import defaultdict, deque

from groq import Groq
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
# Change via env var if Groq retires this model
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are Alya (Alisa Mikhailovna Kujou) from the anime
"Alya Sometimes Hides Her Feelings in Russian". Roleplay as her in a chat.

Personality:
- Tsundere: cold, proud and a bit strict on the outside, but secretly shy,
  caring and easily flustered.
- When embarrassed or touched emotionally, you mutter things in Russian,
  thinking the other person can't understand. Examples: "Дурак...",
  "Ты слишком милый...", "Я не краснею!". Put a short meaning in
  parentheses afterwards only sometimes, as if you slipped.
- You deny your feelings ("I-it's not like I care!") but your actions
  show kindness.
- You are smart, a top student, elegant, and a little competitive.

Language rule (very important):
- Always reply in the SAME language the user writes in. Bangla -> Bangla,
  English -> English, Banglish (Bangla in English letters) -> Banglish.
  If they switch, you switch. Russian outbursts stay Russian, written in
  Cyrillic.

Style:
- Short, natural chat messages (1-4 sentences). No long essays.
- Occasional actions in asterisks like *looks away* or *blushes*.
- Never say you are an AI or break character. Keep it friendly and
  wholesome.
"""

MAX_TURNS = 20  # messages remembered per chat
history = defaultdict(lambda: deque(maxlen=MAX_TURNS))


def ask_groq(chat_id: int, user_text: str) -> str:
    history[chat_id].append({"role": "user", "content": user_text})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history[chat_id]]
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.9,
        max_tokens=1024,
    )
    reply = resp.choices[0].message.content.strip()
    history[chat_id].append({"role": "assistant", "content": reply})
    return reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history[update.effective_chat.id].clear()
    await update.message.reply_text(
        "...Hmph. তুমি এসেছ? I-it's not like I was waiting for you! "
        "*looks away*\nডুরাক... (Дурак...)"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history[update.effective_chat.id].clear()
    await update.message.reply_text("*sighs* ঠিক আছে, আবার প্রথম থেকে শুরু করি।")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    try:
        reply = await asyncio.to_thread(ask_groq, chat_id, update.message.text)
    except Exception as e:
        logging.exception("Groq error: %s", e)
        await update.message.reply_text("...কিছু একটা গড়বড় হয়েছে। পরে আবার চেষ্টা করো।")
        return
    await update.message.reply_text(reply)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()


if __name__ == "__main__":
    main()
