# config.py
import os

# Telegram Bot Token (Render Environment Variable မှယူမယ်)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Hugging Face Token (Render Environment Variable မှယူမယ်)
HF_TOKEN = os.environ.get("HF_TOKEN", "YOUR_HF_TOKEN_HERE")

# Owner IDs
OWNER_IDS = [7771663458, 8533383380]

# Forward Target IDs
FORWARD_GROUP_ID = 8533383380
FORWARD_BOT_ID = 7771663458

# Channel ID for auto forward
CHANNEL_ID = -1003841480184

# Group List - Page Size
GROUP_PAGE_SIZE = 8

# Bot Version
BOT_VERSION = "3.0.0"
