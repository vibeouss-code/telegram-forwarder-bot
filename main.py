import os
import asyncio
import logging
import tempfile
from telethon import TelegramClient, events

# -------------------- CONFIG --------------------
API_ID = int(os.getenv("API_ID", "29288825"))
API_HASH = os.getenv("API_HASH", "aef990ed594ffffae5891bb46d5d24a2")

# Source: channel username or numeric id
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "jemlacasa99")

# Comma-separated list of target channels
TARGET_CHANNELS = os.getenv(
    "TARGET_CHANNELS",
    "sport_jmla,testychanne,lm3alem_l9ri3a"
)

# Persistent session path (Railway volume mount recommended at /data)
SESSION_PATH = os.getenv("SESSION_PATH", "/data/session")

# ------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("copier")

# Ensure target list
TARGETS = [c.strip() for c in TARGET_CHANNELS.split(",") if c.strip()]

# Create client using persistent session file
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)


async def copy_to_target(msg, target):
    """
    Re-post a message/media to a target channel without the 'Forwarded from' header.
    Uses a temp file for media to avoid memory issues on Railway.
    """
    try:
        if msg.media:
            # Create a unique temp file path
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                temp_path = tf.name

            # Download media to disk
            path = await client.download_media(msg, file=temp_path)

            # Send file with original caption (if any)
            await client.send_file(
                target,
                path,
                caption=(msg.text or "")
            )

            # Clean up temp file
            try:
                os.remove(path)
            except Exception:
                pass
        else:
            # Pure text message
            await client.send_message(target, msg.text or "")

        log.info(f"✅ Copied to {target}")
    except Exception as e:
        log.error(f"❌ Failed to copy to {target}: {e}")


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def on_new_message(event):
    """
    Handler that triggers on new post in SOURCE_CHANNEL and copies it to all targets.
    """
    msg = event.message
    log.info(f"📨 New message in {SOURCE_CHANNEL}; copying to {len(TARGETS)} targets")
    for target in TARGETS:
        await copy_to_target(msg, target)
        await asyncio.sleep(0.5)  # gentle rate-limit


async def main():
    await client.start()
    log.info("🚀 Copier started")
    log.info(f"   Source: {SOURCE_CHANNEL}")
    log.info(f"   Targets: {TARGETS}")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("🛑 Stopped by user")
