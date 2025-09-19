import asyncio
import logging
import os
from telethon import TelegramClient, events
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiChannelCopier:
    def __init__(self):
        # Use your provided IDs and channels
        self.api_id = int(os.getenv('API_ID', '29288825'))
        self.api_hash = os.getenv('API_HASH', 'aef990ed594ffffae5891bb46d5d24a2')
        self.source_channel = os.getenv('SOURCE_CHANNEL', 'jemlacasa99')
        
        # Multiple target channels (comma-separated)
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
            logger.info("🚀 Starting Multi-Channel Copier...")
            await self.client.start()
            
            # Get source channel
            self.source_entity = await self.client.get_entity(self.source_channel)
            logger.info(f"📡 Source Channel: {self.source_entity.title}")
            
            # Get all target channels
            self.target_entities = []
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
            
            logger.info(f"✅ Ready to COPY from 1 source to {len(self.target_entities)} targets")
            
            # Handle new messages
            @self.client.on(events.NewMessage(chats=self.source_entity, func=lambda e: e.grouped_id is None))
            async def copy_single_message(event):
                await self.copy_to_all_channels(event.message)

            @self.client.on(events.Album(chats=self.source_entity))
            async def copy_album(event):
                await self.copy_album_to_all_channels(event.messages)
            
            logger.info("✅ Copier active - monitoring messages!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    async def copy_to_all_channels(self, msg):
        """Copy single message (no forward header)"""
        ts = datetime.now().strftime('%H:%M:%S')
        logger.info(f"📨 [{ts}] Copying single message...")

        text = msg.message or ""
        entities = msg.entities

        for i, target in enumerate(self.target_entities, 1):
            try:
                if msg.media:
                    # Download media and re-upload
                    data = await self.client.download_media(msg, bytes)
                    await self.client.send_file(
                        target,
                        data,
                        caption=text,
                        entities=entities,
                        parse_mode=None
                    )
                else:
                    await self.client.send_message(
                        target,
                        text,
                        entities=entities,
                        link_preview=msg.web_preview is not None
                    )

                logger.info(f"✅ Copied to {target.title}")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ Failed to copy to {target.title}: {e}")

    async def copy_album_to_all_channels(self, album_msgs):
        """Copy album (media group) without forward header"""
        captions = [m.message for m in album_msgs if m.message]
        caption = captions[0] if captions else None
        files = [await self.client.download_media(m, bytes) for m in album_msgs if m.media]

        for target in self.target_entities:
            try:
                await self.client.send_file(target, files, caption=caption)
                logger.info(f"✅ Copied album to {target.title}")
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"❌ Album copy failed to {target.title}: {e}")
    
    async def run_forever(self):
        """Run with automatic reconnection"""
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

async def health_check():
    while True:
        await asyncio.sleep(1800)
        logger.info("💚 Multi-Channel Copier running smoothly...")

async def main():
    print("=" * 70)
    print("🤖 MULTI-CHANNEL TELEGRAM COPIER (no forward header)")
    print("=" * 70)
    print("📋 Config:")
    print("   • API_ID - 29288825")
    print("   • API_HASH - aef990ed594ffffae5891bb46d5d24a2")
    print("   • SOURCE_CHANNEL - jemlacasa99")
    print("   • TARGET_CHANNELS - sport_jmla, testychanne, lm3alem_l9ri3a")
    print("=" * 70)
    
    copier = MultiChannelCopier()
    await asyncio.gather(
        copier.run_forever(),
        health_check(),
        return_exceptions=True
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        sys.exit(1)
