import os
import asyncio
import logging
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# মডেল বন্ধ হলে কোড না ছুঁয়ে শুধু GROQ_MODEL এনভায়রনমেন্ট ভেরিয়েবল বদলান
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
