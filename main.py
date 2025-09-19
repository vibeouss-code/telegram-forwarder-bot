import asyncio
import logging
import os
from telethon import TelegramClient, events

# --- CONFIG ---
API_ID = int(os.getenv("API_ID", "29288825"))
API_HASH = os.getenv("API_HASH", "aef990ed594ffffae5891bb46d5d24a2")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "jemlacasa99")
TARGET_CHANNELS = os.getenv("TARGET_CHANNELS", "sport_jmla,testychanne,lm3alem_l9ri3a")

# Split target list
TARGET_CHANNELS = [c.strip() for c in TARGET_CHANNELS.split(",") if c.strip()]

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- TELETHON CLIENT ---
client = TelegramClient("session", API_ID, API_HASH)


async def copy_message(msg, target):
    """Copy message/media without forward header."""
    try:
        if msg.media:
            # Save
