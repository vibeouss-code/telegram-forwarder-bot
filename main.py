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

class TelegramForwarder:
    def __init__(self):
        # Get from environment variables
        self.api_id = int(os.getenv('API_ID', '0'))
        self.api_hash = os.getenv('API_HASH', '')
        self.source_channel = os.getenv('SOURCE_CHANNEL', 'sport_jmla')
        self.target_channel = os.getenv('TARGET_CHANNEL', 'jemlacasa99')
        
        if not self.api_id or not self.api_hash:
            logger.error("❌ Please set API_ID and API_HASH environment variables!")
            sys.exit(1)
        
        self.client = TelegramClient('session', self.api_id, self.api_hash)
    
    async def start(self):
        try:
            logger.info("🚀 Starting bot on Railway...")
            await self.client.start()
            
            # Get channels
            self.source = await self.client.get_entity(self.source_channel)
            self.target = await self.client.get_entity(self.target_channel)
            
            logger.info(f"📡 Source: {self.source.title}")
            logger.info(f"🎯 Target: {self.target.title}")
            
            # Handle new messages
            @self.client.on(events.NewMessage(chats=self.source))
            async def forward_message(event):
                try:
                    await self.client.forward_messages(
                        self.target, event.message, self.source
                    )
                    logger.info("✅ Message forwarded!")
                except Exception as e:
                    logger.error(f"❌ Forward error: {e}")
            
            logger.info("✅ Bot active - monitoring messages!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    async def run_forever(self):
        while True:
            try:
                if await self.start():
                    await self.client.run_until_disconnected()
            except Exception as e:
                logger.error(f"💥 Disconnected: {e}")
                await asyncio.sleep(30)
            
            if self.client.is_connected():
                await self.client.disconnect()
            await asyncio.sleep(10)

async def main():
    print("🤖 Telegram Forwarder - Railway Edition")
    forwarder = TelegramForwarder()
    await forwarder.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
