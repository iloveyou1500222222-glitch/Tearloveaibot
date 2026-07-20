# handlers/admin_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from config import OWNER_IDS
from database import Database

db = Database()

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ ဘန်းချင်သူ့စာကို reply ထောက်ပြီး `/ban` ရေးပါ")
        return
    
    target = update.message.reply_to_message.from_user
    target_id = target.id
    
    if target_id in OWNER_IDS:
        await update.message.reply_text("❌ Owner ကိုဘန်းလို့မရပါ")
        return
    
    try:
        await context.bot.ban_chat_member(chat_id, target_id)
        db.ban_user(chat_id, target_id)
        
        target_name = target.full_name or target.username or "Unknown"
        target_username = f"@{target.username}" if target.username else "N/A"
        
        await update.message.reply_text(
            f"😰 တစ်စုံတစ်ဉီးမှ ကြိုပြောထားသော်လည်း\n"
            f"😪 ထွက်ခွာချင်တဲ့ ငှက်လေးရယ်\n"
            f"🥺 ပြန်မလာနဲတော့\n"
            f"🥀🥀\n"
            f"🚫 ဘန်းခံရသူ: {target_name} ({target_username})\n"
            f"🆔 {target_id}\n"
            f"👤 ဘန်းခဲ့သူ: {update.effective_user.full_name}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ ဘန်းလို့မရပါ: {str(e)[:100]}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Mute ချင်သူ့စာကို reply ထောက်ပြီး `/mute` ရေးပါ")
        return
    
    target = update.message.reply_to_message.from_user
    target_id = target.id
    
    if target_id in OWNER_IDS:
        await update.message.reply_text("❌ Owner ကို mute လို့မရပါ")
        return
    
    try:
        until_date = datetime.now() + timedelta(minutes=3)
        await context.bot.restrict_chat_member(
            chat_id, target_id,
            permissions={"can_send_messages": False},
            until_date=until_date
        )
        
        target_name = target.full_name or target.username or "Unknown"
        target_username = f"@{target.username}" if target.username else "N/A"
        
        await update.message.reply_text(
            f"🔇 {target_name} ({target_username}) ကို ၃မိနစ် Mute လုပ်ထားပါသည်\n"
            f"⏰ {until_date.strftime('%H:%M:%S')} မှာ ပြန်ဖွင့်ပေးပါမည်"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Mute လို့မရပါ: {str(e)[:100]}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Unmute ချင်သူ့စာကို reply ထောက်ပြီး `/unmute` ရေးပါ")
        return
    
    target = update.message.reply_to_message.from_user
    target_id = target.id
    
    try:
        await context.bot.restrict_chat_member(
            chat_id, target_id,
            permissions={"can_send_messages": True}
        )
        db.reset_warning(chat_id, target_id)
        
        target_name = target.full_name or target.username or "Unknown"
        await update.message.reply_text(f"✅ {target_name} ကို Unmute လုပ်ပြီးပါပြီ")
    except Exception as e:
        await update.message.reply_text(f"❌ Unmute လို့မရပါ: {str(e)[:100]}")

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
