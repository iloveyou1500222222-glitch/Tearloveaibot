# handlers/forward_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from config import OWNER_IDS, FORWARD_GROUP_ID, FORWARD_BOT_ID

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE, message_type="group"):
    chat_id = update.effective_chat.id
    user = update.effective_user
    message = update.message
    
    name = user.full_name or user.username or "Unknown"
    user_id = user.id
    username = f"@{user.username}" if user.username else "N/A"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if message.text:
        content = message.text
    elif message.caption:
        content = message.caption
    elif message.sticker:
        content = f"[Sticker: {message.sticker.emoji}]"
    elif message.photo:
        content = "[Photo]"
    elif message.video:
        content = "[Video]"
    else:
        content = "[Media]"
    
    forward_text = f"""📨 **အသုံးပြုသူထံမှ**

👤 **အမည်:** {name}
🆔 **ID:** {user_id}
📛 **Username:** {username}
📅 **ရက်စွဲ:** {current_time}
📍 **Chat:** {chat_id}

💬 **မေးခွန်း:**
{content}

{'='*30}
🤖 **Bot အဖြေ:**
"""
    
    if context.user_data.get('last_ai_reply'):
        forward_text += context.user_data.get('last_ai_reply')
    else:
        forward_text += "အဖြေမရှိသေးပါ"
    
    for owner_id in OWNER_IDS:
        try:
            await context.bot.send_message(owner_id, forward_text[:4096])
        except:
            pass
