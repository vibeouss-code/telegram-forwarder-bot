# requirements.txt MUST include: telethon==1.34.0

import asyncio
import logging
import os
import sys
import tempfile
from datetime import datetime

try:
    from telethon import TelegramClient, events
except ModuleNotFoundError:
    print("\n❌ ERROR: 'telethon' module not found. Make sure to install it using:")
    print("   pip install telethon==1.34.0\n")
    sys.exit(1)

# ---------------- Logging Setup ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------- Bot Class ----------------
class MultiChannelPoster:
    def __init__(self):
        self.api_id = int(os.getenv('API_ID', '29288825'))
        self.api_hash = os.getenv('API_HASH', 'aef990ed594ffffae5891bb46d5d24a2')
        self.source_channel = os.getenv('SOURCE_CHANNEL', 'jemlacasa99')
        target_channels_str = os.getenv('TARGET_CHANNELS', 'sport_jmla,testychanne,lm3alem_l9ri3a')
        self.target_channels = [ch.strip() for ch in target_channels_str.split(',') if ch.strip()]

        if not self.api_id or not self.api_hash:
            logger.error("❌ Please set API_ID and API_HASH environment variables!")
            sys.exit(1)

        if not self.target_channels:
            logger.error("❌ Please set TARGET_CHANNELS environment variable!")
            sys.exit(1)

        self.client = TelegramClient('session', self.api_id, self.api_hash)
        self.source_entity = None
        self.target_entities = []

    async def start(self):
        try:
            logger.info("🚀 Starting Multi-Channel Poster...")
            await self.client.start()
            self.source_entity = await self.client.get_entity(self.source_channel)
            logger.info(f"📡 Source Channel: {self.source_entity.title}")

            for i, channel in enumerate(self.target_channels, 1):
                try:
                    entity = await self.client.get_entity(channel)
                    self.target_entities.append(entity)
                    logger.info(f"🎯 Target {i}: {entity.title}")
                except Exception as e:
                    logger.error(f"❌ Failed to get channel '{channel}': {e}")

            if not self.target_entities:
                logger.error("❌ No valid target channels found!")
                return False

            @self.client.on(events.NewMessage(chats=self.source_entity))
            async def handle_new_message(event):
                await self.copy_to_all_channels(event.message)

            logger.info("✅ Bot active - monitoring messages!")
            return True

        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False

    async def copy_to_all_channels(self, msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        logger.info(f"📨 [{timestamp}] New message detected - copying to {len(self.target_entities)} channels...")

        for i, target in enumerate(self.target_entities, 1):
            try:
                if msg.media:
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                          path = await self.client.download_media(msg, file=tmp.name)
                    await self.client.send_file(target, path, caption=(msg.text or ""), force_document=False)
                      os.remove(path)
                else:
                    await self.client.send_message(target, msg.text or "")

                logger.info(f"✅ [{timestamp}] Posted to channel {i}: {target.title}")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ [{timestamp}] Failed to post to {target.title}: {e}")

    async def run_forever(self):
        while True:
            try:
                if await self.start():
                    await self.client.run_until_disconnected()
            except Exception as e:
                logger.error(f"💥 Disconnected: {e}")
                logger.info("🔄 Reconnecting in 30 seconds...")
                await asyncio.sleep(30)
            if self.client.is_connected():
                await self.client.disconnect()
            logger.info("🔄 Attempting to restart...")
            await asyncio.sleep(10)

# ---------------- Health Check ----------------
async def health_check():
    while True:
        await asyncio.sleep(1800)
        logger.info("💚 Multi-Channel Poster running smoothly...")

# ---------------- Entrypoint ----------------
async def main():
    print("=" * 70)
    print("🤖 MULTI-CHANNEL TELEGRAM POSTER")
    print("=" * 70)
    poster = MultiChannelPoster()
    await asyncio.gather(
        poster.run_forever(),
        health_check(),
        return_exceptions=True
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        sys.exit(1)
