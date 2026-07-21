import os
import sys
import logging
import asyncio
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

# ===== Python version print =====
print(f"🐍 Python version: {sys.version}")

try:
    from telegram import Update
    from telegram.ext import (
        ApplicationBuilder, ContextTypes, MessageHandler,
        CommandHandler, CallbackQueryHandler, filters
    )
    print("✅ Telegram import successful")
except Exception as e:
    print(f"❌ Telegram import error: {e}")
    sys.exit(1)

try:
    from config import BOT_TOKEN, OWNER_IDS, BOT_VERSION, CHANNEL_ID
    from database import Database
    print("✅ Config import successful")
except Exception as e:
    print(f"❌ Config import error: {e}")
    sys.exit(1)

# ===== Import Handlers =====
try:
    from handlers.ai_handler import ai_command, ai_chat
    from handlers.welcome_handler import set_welcome, delete_welcome_video, delete_welcome_text, set_welcome_text, greet_new_member
    from handlers.admin_handler import ban_user, mute_user, unmute_user
    from handlers.forward_handler import forward_to_owner
    from handlers.teach_handler import teach_command, q_command, a_command, teacher_command
    from handlers.call_handler import call_all, call_settings, call_button_handler
    from handlers.rule_handler import set_rule, get_rule, delete_rule
    from handlers.anti_spam import check_spam
    from handlers.button_handler import button_handler, start_buttons, help_system
    from handlers.broadcast_handler import broadcast, add_group, remove_group, list_groups
    from handlers.group_list_handler import my_groups, group_page_callback
    from handlers.broadcast_code_handler import create_broadcast_code, use_broadcast_code
    from handlers.channel_auto_handler import channel_auto_forward
    from handlers.bot_manager import bot_sosar, botcoline, botlist, botdm, botremove, botcheck
    print("✅ Handlers import successful")
except Exception as e:
    print(f"❌ Handlers import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===== Logging =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

# ===== Flask App for Render Keep-Alive =====
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return jsonify({
        "status": "alive",
        "version": BOT_VERSION,
        "time": datetime.now().isoformat(),
        "bot": "@Group_ai_help_bot"
    })

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ===== Essential Commands =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""👋 မဂ်လာပါ {user.first_name}!

🤖 ကျွန်တော်က AI Group Helper Bot ပါ။

📚 အသုံးပြုနည်း:
• Group: /ai [မေးခွန်း]
• Private: စာရိုက်ရုံနဲ့ AI ဖြေမယ်
• /start - ဒီစာကိုပြမယ်
• /help - အသုံးပြုပုံအပြည့်အစုံ

👤 Owner: @Tear808
📢 Channel: @BOTUAPTE"""
    keyboard = await start_buttons(update, context)
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def main_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await help_system(update, context)

def main():
    # 1. Start Flask
    Thread(target=run_flask, daemon=True).start()
    print("🌐 Flask server is running")

    # 2. Build Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # ===== Register Handlers =====
    
    # Basic Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", main_help))
    
    # AI Handlers
    application.add_handler(CommandHandler("ai", ai_command))
    
    # Admin & Management
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    
    # Welcome & Rules
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
    application.add_handler(CommandHandler("setrule", set_rule))
    application.add_handler(CommandHandler("rule", get_rule))
    
    # Broadcast & Groups
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("mygroups", my_groups))
    
    # Callback Query (Buttons)
    application.add_handler(CallbackQueryHandler(button_handler))

    # AI Chat logic (Private message)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    # 3. Start Bot
    print("🤖 Bot started successfully!")
    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
