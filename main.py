# main.py
import os
import sys
import logging
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

print(f"🐍 Python version: {sys.version}")

# ===== Telegram Import (python-telegram-bot 13.7 အတွက်) =====
try:
    from telegram import Update, Bot
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    print("✅ Telegram import successful")
except Exception as e:
    print(f"❌ Telegram import error: {e}")
    sys.exit(1)

# ===== Config & Database =====
try:
    from config import BOT_TOKEN, OWNER_IDS, BOT_VERSION, CHANNEL_ID
    from database import Database
    print("✅ Config import successful")
except Exception as e:
    print(f"❌ Config import error: {e}")
    sys.exit(1)

# ===== Handlers =====
try:
    from handlers.ai_handler import ai_command, ai_chat, get_ai_response
    from handlers.welcome_handler import set_welcome, delete_welcome_video, delete_welcome_text, set_welcome_text, greet_new_member, is_admin_or_owner
    from handlers.admin_handler import ban_user, mute_user, unmute_user
    from handlers.forward_handler import forward_to_owner
    from handlers.teach_handler import teach_command, q_command, a_command, teacher_command
    from handlers.call_handler import call_all, call_settings, call_button_handler
    from handlers.rule_handler import set_rule, get_rule, delete_rule
    from handlers.anti_spam import check_spam
    from handlers.button_handler import button_handler, start_buttons, more_buttons, help_system, back_to_start
    from handlers.broadcast_handler import broadcast, add_group, remove_group, list_groups
    from handlers.group_list_handler import my_groups, group_page_callback
    from handlers.broadcast_code_handler import create_broadcast_code, use_broadcast_code, list_broadcast_codes
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
def start(update: Update, context: CallbackContext):
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
    
    keyboard = start_buttons(update, context)
    update.message.reply_text(welcome_text, reply_markup=keyboard)

# ===== Help Command =====
def help_command(update: Update, context: CallbackContext):
    help_system(update, context)

# ===== Message Handler for Broadcast Code =====
def check_broadcast_code(update: Update, context: CallbackContext):
    text = update.message.text
    if not text:
        return
    
    import re
    if re.match(r'^[A-Z0-9]{8}\s+.+', text):
        use_broadcast_code(update, context)

# ===== Main =====
def main():
    try:
        # Start Flask thread
        Thread(target=run_flask, daemon=True).start()
        logger.info("🚀 Flask server started")
        
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not set!")
            return
        
        # ===== Updater (python-telegram-bot 13.7 အတွက်) =====
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # ===== Command Handlers =====
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("ai", ai_command))
        dp.add_handler(CommandHandler("setwelcome", set_welcome))
        dp.add_handler(CommandHandler("deletevideo", delete_welcome_video))
        dp.add_handler(CommandHandler("deleteshortstory", delete_welcome_text))
        dp.add_handler(CommandHandler("shortstory", set_welcome_text))
        dp.add_handler(CommandHandler("setrule", set_rule))
        dp.add_handler(CommandHandler("gprue", get_rule))
        dp.add_handler(CommandHandler("deaterue", delete_rule))
        dp.add_handler(CommandHandler("teach", teach_command))
        dp.add_handler(CommandHandler("q", q_command))
        dp.add_handler(CommandHandler("a", a_command))
        dp.add_handler(CommandHandler("teacher", teacher_command))
        dp.add_handler(CommandHandler("call", call_all))
        dp.add_handler(CommandHandler("callsetting", call_settings))
        dp.add_handler(CommandHandler("ban", ban_user))
        dp.add_handler(CommandHandler("mute", mute_user))
        dp.add_handler(CommandHandler("unmute", unmute_user))
        dp.add_handler(CommandHandler("bcast", broadcast))
        dp.add_handler(CommandHandler("addgroup", add_group))
        dp.add_handler(CommandHandler("removegroup", remove_group))
        dp.add_handler(CommandHandler("listgroups", list_groups))
        dp.add_handler(CommandHandler("mygroups", my_groups))
        dp.add_handler(CommandHandler("timebc", create_broadcast_code))
        dp.add_handler(CommandHandler("timetear", list_broadcast_codes))
        dp.add_handler(CommandHandler("botsosar", bot_sosar))
        dp.add_handler(CommandHandler("botcoline", botcoline))
        dp.add_handler(CommandHandler("botlist", botlist))
        dp.add_handler(CommandHandler("botdm", botdm))
        dp.add_handler(CommandHandler("botremove", botremove))
        dp.add_handler(CommandHandler("botcheck", botcheck))
        
        # ===== Message Handlers =====
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.private, ai_chat))
        dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, greet_new_member))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_broadcast_code))
        
        # ===== Channel Auto Forward =====
        # (python-telegram-bot 13.7 မှာ channel_post အတွက် handler ထည့်နည်း)
        
        # ===== Callback Handler =====
        dp.add_handler(CallbackQueryHandler(button_handler))
        dp.add_handler(CallbackQueryHandler(group_page_callback, pattern="^group_page_"))
        dp.add_handler(CallbackQueryHandler(call_button_handler, pattern="^call_"))
        
        # ===== Error Handler =====
        def error_handler(update, context):
            logger.error(f"💥 Error: {context.error}")
            if update and update.effective_message:
                update.effective_message.reply_text(
                    "❌ နည်းပညာပိုင်းဆိုင်ရာ အမှားတစ်ခုဖြစ်သွားပါပြီ။\n"
                    "👤 Owner ကို ဆက်သွယ်ပါ။ @Tear808"
                )
        
        dp.add_error_handler(error_handler)
        
        logger.info(f"🤖 Bot started! Version: {BOT_VERSION}")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"💥 Main error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
