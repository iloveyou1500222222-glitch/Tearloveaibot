# handlers/rule_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from config import OWNER_IDS

db = Database()

async def set_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ စည်းကမ်းစာကို reply ထောက်ပြီး `/setrule` ရေးပါရှင့်")
        return
    
    rule_text = update.message.reply_to_message.text
    if not rule_text:
        await update.message.reply_text("❌ စာသားကိုသာ သတ်မှတ်နိုင်ပါတယ်")
        return
    
    db.set_rule(chat_id, rule_text)
    await update.message.reply_text("✅ စည်းကမ်းသတ်မှတ်ပြီးပါပြီရှင့်")

async def get_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rule = db.get_rule(chat_id)
    
    if rule:
        await update.message.reply_text(f"📜 **Group စည်းကမ်း**\n\n{rule}")
    else:
        await update.message.reply_text("❌ စည်းကမ်းမရှိသေးပါ")

async def delete_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    db.delete_rule(chat_id)
    await update.message.reply_text("✅ စည်းကမ်းဖျက်ပြီးပါပြီ")

async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id in OWNER_IDS:
        return True
    
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == user_id:
                return True
    except:
        pass
    
    return False
