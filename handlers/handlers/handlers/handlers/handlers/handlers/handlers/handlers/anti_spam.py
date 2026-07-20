# handlers/anti_spam.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from database import Database
from config import OWNER_IDS

db = Database()

async def check_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message = update.message
    
    if await is_admin_or_owner(update, context):
        return
    
    is_muted, mute_until = db.is_muted(chat_id, user_id)
    if is_muted:
        await message.delete()
        await message.reply_text(
            f"🔇 သင်က mute ခံထားရပါသေးတယ်။\n"
            f"⏰ {mute_until.strftime('%H:%M:%S')} မှာ ပြန်ဖွင့်ပေးပါမည်"
        )
        return
    
    has_link = False
    if message.text and ("http://" in message.text or "https://" in message.text or "t.me/" in message.text):
        has_link = True
    
    is_forward = bool(message.forward_date)
    
    if has_link or is_forward:
        warning = db.increment_warning(chat_id, user_id)
        count = warning['count']
        
        if count == 1:
            await message.reply_text(
                f"⚠️ Link/Forward မချရဘူးနော် စည်းကမ်းရှိပါ (@Tear808)\n"
                f"ချချင်ရင်ခွင့်တောင်းပါ Group အရာရှိတွေကို"
            )
        elif count == 2:
            await message.reply_text(
                f"⚠️ ၂ခါရှိပီးနော် \"၃\"ခါပြည့်ရင် (@Tear808) အပစ်ပေးခံရမယ်မိတ်ဆွေ"
            )
            await message.delete()
        elif count >= 3:
            until_date = datetime.now() + timedelta(minutes=3)
            try:
                await context.bot.restrict_chat_member(
                    chat_id, user_id,
                    permissions={"can_send_messages": False},
                    until_date=until_date
                )
                await message.reply_text(
                    f"🔇 စည်ကမ်းချိုးဖောက်ပါသဖြင့် (@Tear808) သင်အားမြူလိုက်ပါပီ\n"
                    f"⏰ ၃မိနစ်ပြည့်မှ စကားပြန်ပြောပါရှင့်"
                )
                await message.delete()
                db.reset_warning(chat_id, user_id)
            except:
                pass

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
