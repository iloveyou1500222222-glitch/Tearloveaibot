# handlers/welcome_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import OWNER_IDS

db = Database()

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Video ကို reply ထောက်ပြီး `/setwelcome` ရေးပါရှင့်")
        return
    
    video = update.message.reply_to_message.video
    if not video:
        await update.message.reply_text("❌ Video ကိုသာ သတ်မှတ်နိုင်ပါတယ်")
        return
    
    text = " ".join(context.args) if context.args else ""
    db.set_welcome(chat_id, video.file_id, text)
    await update.message.reply_text(f"✅ Welcome video သတ်မှတ်ပြီးပါပြီ\n📝 စာ: {text if text else 'မပါ'}")

async def set_welcome_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("❌ `/shortstory ကြိုဆိုစာ` လို့ရေးပါ")
        return
    
    db.set_welcome_text(chat_id, text)
    await update.message.reply_text(f"✅ Welcome text သတ်မှတ်ပြီးပါပြီ\n📝 စာ: {text}")

async def delete_welcome_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    db.delete_welcome(chat_id)
    await update.message.reply_text("✅ Welcome video ဖျက်ပြီးပါပြီ")

async def delete_welcome_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not (await is_admin_or_owner(update, context)):
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    welcome = db.get_welcome(chat_id)
    if welcome:
        db.set_welcome(chat_id, welcome['video_id'], "")
        await update.message.reply_text("✅ Welcome text ဖျက်ပြီးပါပြီ")

async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    for member in update.message.new_chat_members:
        welcome = db.get_welcome(chat_id)
        
        name = member.full_name or member.username or "Unknown"
        user_id = member.id
        username = f"@{member.username}" if member.username else "N/A"
        bio = member.bio if hasattr(member, 'bio') and member.bio else "N/A"
        
        keyboard = [[InlineKeyboardButton("👥 Admin ကြည့်ရန်", callback_data=f"admin_list_{chat_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        caption = f"👋 မဂ်လာပါ {name}!\n🆔 {user_id}\n📛 {username}\n📝 Bio: {bio}\n\n"
        
        if welcome and welcome['text']:
            caption += welcome['text']
        else:
            caption += "💓 Group မှာ ပျော်ပျော်နေနော် 👉❤👈"
        
        if welcome and welcome['video_id']:
            await context.bot.send_video(
                chat_id=chat_id,
                video=welcome['video_id'],
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            photos = await context.bot.get_user_profile_photos(member.id, limit=1)
            if photos.total_count > 0:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photos.photos[0][0].file_id,
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(caption, reply_markup=reply_markup)

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
