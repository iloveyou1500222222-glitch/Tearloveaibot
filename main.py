# main.py
import os
import logging
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler,
    CommandHandler, CallbackQueryHandler, filters
)

from config import BOT_TOKEN, OWNER_IDS, BOT_VERSION, CHANNEL_ID
from handlers import *
from database import Database

# ===== Logging =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

# ===== Flask App =====
flask_app = Flask('')

@flask_app.route('/')
def home():
    return jsonify({
        "status": "alive",
        "version": BOT_VERSION,
        "time": datetime.now().isoformat(),
        "bot": "@Group_ai_help_bot"
    })

@flask_app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ===== Start Command =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""👋 မဂ်လာပါ {user.first_name}!

🤖 ကျွန်တော်က **AI Group Helper Bot** ပါ။

📚 **အသုံးပြုနည်း:**
• Group: `/ai [မေးခွန်း]`
• Private: စာရိုက်ရုံနဲ့ AI ဖြေမယ်
• `/start` - ဒီစာကိုပြမယ်
• `/help` - အသုံးပြုပုံအပြည့်အစုံ

👤 **Owner:** @Tear808
📢 **Channel:** @BOTUAPTE

ဘာမေးချင်လဲ ရေးပါ..."""
    
    keyboard = await start_buttons(update, context)
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# ===== Help Command =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await help_system(update, context)

# ===== Message Handler for Broadcast Code =====
async def check_broadcast_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    
    import re
    if re.match(r'^[A-Z0-9]{8}\s+.+', text):
        await use_broadcast_code(update, context)

# ===== Main =====
def main():
    # Start Flask thread
    Thread(target=run_flask, daemon=True).start()
    logger.info("🚀 Flask server started")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # ===== Command Handlers =====
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("setwelcome", set_welcome))
    application.add_handler(CommandHandler("deletevideo", delete_welcome_video))
    application.add_handler(CommandHandler("deleteshortstory", delete_welcome_text))
    application.add_handler(CommandHandler("shortstory", set_welcome_text))
    application.add_handler(CommandHandler("setrule", set_rule))
    application.add_handler(CommandHandler("gprue", get_rule))
    application.add_handler(CommandHandler("deaterue", delete_rule))
    application.add_handler(CommandHandler("teach", teach_command))
    application.add_handler(CommandHandler("q", q_command))
    application.add_handler(CommandHandler("a", a_command))
    application.add_handler(CommandHandler("teacher", teacher_command))
    application.add_handler(CommandHandler("call", call_all))
    application.add_handler(CommandHandler("callsetting", call_settings))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    application.add_handler(CommandHandler("bcast", broadcast))
    application.add_handler(CommandHandler("addgroup", add_group))
    application.add_handler(CommandHandler("removegroup", remove_group))
    application.add_handler(CommandHandler("listgroups", list_groups))
    application.add_handler(CommandHandler("mygroups", my_groups))
    application.add_handler(CommandHandler("timebc", create_broadcast_code))
    application.add_handler(CommandHandler("timetear", list_broadcast_codes))
    
    # Bot Manager System
    application.add_handler(CommandHandler("botsosar", bot_sosar))
    application.add_handler(CommandHandler("botcoline", botcoline))
    application.add_handler(CommandHandler("botlist", botlist))
    application.add_handler(CommandHandler("botdm", botdm))
    application.add_handler(CommandHandler("botremove", botremove))
    application.add_handler(CommandHandler("botcheck", botcheck))
    
    # ===== Message Handlers =====
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, ai_chat))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_broadcast_code))
    
    # ===== Channel Auto Forward =====
    application.add_handler(
        MessageHandler(
            filters.Chat(chat_id=CHANNEL_ID) & filters.UpdateType.CHANNEL_POST,
            channel_auto_forward
        )
    )
    
    # ===== Callback Handler =====
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(group_page_callback, pattern="^group_page_"))
    application.add_handler(CallbackQueryHandler(call_button_handler, pattern="^call_"))
    
    # ===== Error Handler =====
    async def error_handler(update, context):
        logger.error(f"💥 Error: {context.error}")
    application.add_error_handler(error_handler)
    
    logger.info(f"🤖 Bot started! Version: {BOT_VERSION}")
    application.run_polling()

if __name__ == "__main__":
    main()
