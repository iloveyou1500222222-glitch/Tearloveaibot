# main.py
import os
import sys
import logging
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

print(f"🐍 Python version: {sys.version}")

# ===== Telegram Import =====
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes
    from telegram.ext import filters as Filters
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
    try:
        Thread(target=run_flask, daemon=True).start()
        logger.info("🚀 Flask server started")
        
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not set!")
            return
        
        application = Application.builder().token(BOT_TOKEN).build()
        
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
        application.add_handler(CommandHandler("botsosar", bot_sosar))
        application.add_handler(CommandHandler("botcoline", botcoline))
        application.add_handler(CommandHandler("botlist", botlist))
        application.add_handler(CommandHandler("botdm", botdm))
        application.add_handler(CommandHandler("botremove", botremove))
        application.add_handler(CommandHandler("botcheck", botcheck))
        
        # ===== Message Handlers =====
        application.add_handler(MessageHandler(Filters.TEXT & ~Filters.COMMAND & Filters.ChatType.PRIVATE, ai_chat))
        application.add_handler(MessageHandler(Filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_member))
        application.add_handler(MessageHandler(Filters.TEXT & ~Filters.COMMAND, check_broadcast_code))
        
        # ===== Channel Auto Forward =====
        application.add_handler(
            MessageHandler(
                Filters.Chat(chat_id=CHANNEL_ID) & Filters.UpdateType.CHANNEL_POST,
                channel_auto_forward
            )
        )
        
        # ===== Callback Handler =====
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(CallbackQueryHandler(group_page_callback, pattern="^group_page_"))
        application.add_handler(CallbackQueryHandler(call_button_handler, pattern="^call_"))
        
        # ===== Error Handler =====
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.error(f"💥 Error: {context.error}")
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ နည်းပညာပိုင်းဆိုင်ရာ အမှားတစ်ခုဖြစ်သွားပါပြီ။\n"
                    "👤 Owner ကို ဆက်သွယ်ပါ။ @Tear808"
                )
        
        application.add_error_handler(error_handler)
        
        logger.info(f"🤖 Bot started! Version: {BOT_VERSION}")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"💥 Main error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
