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

class MultiChannelPoster:
    def __init__(self):
        # Get from environment variables
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.source_channel = os.getenv('SOURCE_CHANNEL', 'testy_jemla')
        
        # Multiple target channels (comma-separated)
        target_channels_str = os.getenv('TARGET_CHANNELS', '')
        self.target_channels = [ch.strip() for ch in target_channels_str.split(',') if ch.strip()]
        
        if not self.api_id or not self.api_hash:
            logger.error("❌ Please set API_ID and API_HASH environment variables!")
            sys.exit(1)
        
        if not self.target_channels:
            logger.error("❌ Please set TARGET_CHANNELS environment variable!")
            sys.exit(1)
        
        # Use the session file we created
        self.client = TelegramClient('railway_session', self.api_id, self.api_hash)
        self.source_entity = None
        self.target_entities = []
    
    async def start(self):
        try:
            logger.info("🚀 Starting Multi-Channel Poster on Railway...")
            await self.client.start()
            
            # Get source channel
            self.source_entity = await self.client.get_entity(self.source_channel)
            logger.info(f"📡 Source Channel: {self.source_entity.title}")
            
            # Get all target channels
            self.target_entities = []
            for i, channel in enumerate(self.target_channels, 1):
                try:
                    logger.info(f"🔍 Connecting to target channel {i}: '{channel}'")
                    entity = await self.client.get_entity(channel)
                    self.target_entities.append(entity)
                    logger.info(f"✅ Target {i}: {entity.title}")
                except Exception as e:
                    logger.error(f"❌ Failed to connect to '{channel}': {e}")
                    logger.error(f"Make sure '{channel}' exists and bot is admin there")
            
            if not self.target_entities:
                logger.error("❌ No valid target channels found!")
                return False
            
            logger.info(f"🎯 Ready to post from 1 source to {len(self.target_entities)} target channels")
            
            # Handle new messages
            @self.client.on(events.NewMessage(chats=self.source_entity))
            async def handle_new_message(event):
                await self.post_to_all_channels(event)
            
            logger.info("✅ Bot is active and monitoring for new posts!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    async def post_to_all_channels(self, event):
        """Post message content directly to all target channels"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = event.message
        
        logger.info(f"📨 [{timestamp}] New message detected!")
        logger.info(f"📝 Content type: {'Text' if message.text and not message.media else 'Media'}")
        
        success_count = 0
        failed_count = 0
        
        for i, target in enumerate(self.target_entities, 1):
            try:
                # Handle different message types
                if message.media:
                    # Post media (photos, videos, documents) with caption
                    await self.client.send_file(
                        target,
                        message.media,
                        caption=message.text if message.text else ""
                    )
                    logger.info(f"✅ [{timestamp}] Posted media to {target.title}")
                
                elif message.text:
                    # Post text only
                    await self.client.send_message(target, message.text)
                    logger.info(f"✅ [{timestamp}] Posted text to {target.title}")
                
                success_count += 1
                
                # Delay to avoid rate limits
                await asyncio.sleep(1.5)
                
            except Exception as e:
                logger.error(f"❌ [{timestamp}] Failed to post to {target.title}: {e}")
                failed_count += 1
        
        logger.info(f"📊 [{timestamp}] Summary: {success_count} successful, {failed_count} failed")
    
    async def run_forever(self):
        """Run with automatic reconnection"""
        while True:
            try:
                if await self.start():
                    await self.client.run_until_disconnected()
            except Exception as e:
                logger.error(f"💥 Connection lost: {e}")
                logger.info("🔄 Reconnecting in 30 seconds...")
                await asyncio.sleep(30)
            
            # Cleanup before retry
            if self.client.is_connected():
                await self.client.disconnect()
            
            logger.info("🔄 Restarting connection...")
            await asyncio.sleep(10)

async def keep_alive():
    """Keep Railway service active"""
    while True:
        await asyncio.sleep(1800)  # 30 minutes
        logger.info("💚 Service running smoothly - posting to multiple channels...")

async def main():
    print("=" * 70)
    print("🤖 MULTI-CHANNEL TELEGRAM POSTER - RAILWAY EDITION")
    print("=" * 70)
    print("📋 Your current settings:")
    print(f"   • Source: {os.getenv('SOURCE_CHANNEL', 'testy_jemla')}")
    print(f"   • Targets: {os.getenv('TARGET_CHANNELS', 'jemla_clothing')}")
    print("=" * 70)
    print("✨ Posts will appear as original content (no forwarding labels)")
    print("=" * 70)
    
    poster = MultiChannelPoster()
    
    # Run poster with keep-alive
    await asyncio.gather(
        poster.run_forever(),
        keep_alive(),
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
