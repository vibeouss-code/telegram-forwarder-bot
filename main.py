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

class MultiChannelForwarder:
    def __init__(self):
        # Get from environment variables
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.source_channel = os.getenv('SOURCE_CHANNEL', 'sport_jmla')
        
        # Multiple target channels (comma-separated)
        target_channels_str = os.getenv('TARGET_CHANNELS', 'jemlacasa99,channel2,lm3alem_l9ri3a')
        self.target_channels = [ch.strip() for ch in target_channels_str.split(',') if ch.strip()]
        
        if not self.api_id or not self.api_hash:
            logger.error("❌ Please set API_ID and API_HASH environment variables!")
            sys.exit(1)
        
        if not self.target_channels:
            logger.error("❌ Please set TARGET_CHANNELS environment variable!")
            sys.exit(1)
        
        self.client = TelegramClient('railway_session', self.api_id, self.api_hash)
        self.source_entity = None
        self.target_entities = []
    
    async def start(self):
        try:
            logger.info("🚀 Starting Multi-Channel Forwarder on Railway...")
            await self.client.start()
            
            # Get source channel
            self.source_entity = await self.client.get_entity(self.source_channel)
            logger.info(f"📡 Source Channel: {self.source_entity.title}")
            
            # Get all target channels
            self.target_entities = []
            for i, channel in enumerate(self.target_channels, 1):
                try:
                    logger.info(f"🔍 Attempting to connect to channel {i}: '{channel}'")
                    entity = await self.client.get_entity(channel)
                    self.target_entities.append(entity)
                    logger.info(f"✅ Successfully connected to Target {i}: {entity.title} (ID: {entity.id})")
                except Exception as e:
                    logger.error(f"❌ Failed to get channel '{channel}': {str(e)}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    # Continue with other channels even if one fails
            
            if not self.target_entities:
                logger.error("❌ No valid target channels found!")
                return False
            
            logger.info(f"✅ Ready to forward from 1 source to {len(self.target_entities)} targets")
            
            # Handle new messages
            @self.client.on(events.NewMessage(chats=self.source_entity))
            async def forward_message(event):
                await self.forward_to_all_channels(event)
            
            logger.info("✅ Bot active - monitoring messages!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    async def post_to_all_channels(self, event):
        """Post message content directly to all target channels (not forward)"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        logger.info(f"📨 [{timestamp}] New message detected - posting to {len(self.target_entities)} channels...")
        
        success_count = 0
        failed_count = 0
        
        message = event.message
        
        for i, target in enumerate(self.target_entities, 1):
            try:
                # Post text messages directly
                if message.text and not message.media:
                    await self.client.send_message(
                        target, 
                        message.text
                    )
                    logger.info(f"✅ [{timestamp}] Posted text to channel {i}: {target.title}")
                
                # Post media (photos, videos, documents) with caption
                elif message.media:
                    await self.client.send_file(
                        target,
                        message.media,
                        caption=message.text if message.text else ""
                    )
                    logger.info(f"✅ [{timestamp}] Posted media to channel {i}: {target.title}")
                
                # Post text with media (both text and media)
                elif message.text and message.media:
                    await self.client.send_file(
                        target,
                        message.media, 
                        caption=message.text
                    )
                    logger.info(f"✅ [{timestamp}] Posted media+text to channel {i}: {target.title}")
                
                success_count += 1
                
                # Delay between posts to avoid rate limits
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"❌ [{timestamp}] Failed to post to {target.title}: {e}")
                failed_count += 1
        
        logger.info(f"📊 [{timestamp}] Post summary: {success_count} success, {failed_count} failed")
    
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
            
            # Cleanup before retry
            if self.client.is_connected():
                await self.client.disconnect()
            
            logger.info("🔄 Attempting to restart...")
            await asyncio.sleep(10)

async def health_check():
    """Keep the service alive"""
    while True:
        await asyncio.sleep(1800)  # 30 minutes
        logger.info("💚 Multi-Channel Forwarder running smoothly...")

async def main():
    print("=" * 70)
    print("🤖 MULTI-CHANNEL TELEGRAM FORWARDER")
    print("=" * 70)
    print("📋 Environment Variables Required:")
    print("   • API_ID - Your Telegram API ID")
    print("   • API_HASH - Your Telegram API Hash") 
    print("   • SOURCE_CHANNEL - Channel to monitor")
    print("   • TARGET_CHANNELS - Comma-separated list of target channels")
    print("=" * 70)
    print("📝 Example TARGET_CHANNELS: channel1,channel2,channel3")
    print("=" * 70)
    
    forwarder = MultiChannelForwarder()
    
    # Run forwarder with health checks
    await asyncio.gather(
        forwarder.run_forever(),
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
