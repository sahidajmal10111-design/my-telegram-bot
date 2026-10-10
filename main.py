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
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
