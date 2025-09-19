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
        self.api_id = int(os.getenv('API_ID', ''))
        self.api_hash = os.getenv('API_HASH', '')
        self.source_channel = os.getenv('SOURCE_CHANNEL', 'jemlacasa99')
        
        # Multiple target channels (comma-separated)
        target_channels_str = os.getenv('TARGET_CHANNELS', 'sport_jmla,channel1,channel2')
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
            logger.info("🚀 Starting Multi-Channel Forwarder on Railway...")
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
    
    async def forward_to_all_channels(self, event):
        """Forward message to all target channels"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        logger.info(f"📨 [{timestamp}] New message detected - forwarding to {len(self.target_entities)} channels...")
        
        success_count = 0
        failed_count = 0
        
        for i, target in enumerate(self.target_entities, 1):
            try:
                await self.client.forward_messages(
                    target, event.message, self.source_entity
                )
                logger.info(f"✅ [{timestamp}] Forwarded to channel {i}: {target.title}")
                success_count += 1
                
                # Small delay between forwards to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ [{timestamp}] Failed to forward to {target.title}: {e}")
                failed_count += 1
        
        logger.info(f"📊 [{timestamp}] Forward summary: {success_count} success, {failed_count} failed")
    
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
    print("   • API_ID - 29288825")
    print("   • API_HASH - aef990ed594ffffae5891bb46d5d24a2") 
    print("   • SOURCE_CHANNEL - jemlacasa99")
    print("   • TARGET_CHANNELS - sport_jmla-testychanne-lm3alem_l9ri3a")
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
