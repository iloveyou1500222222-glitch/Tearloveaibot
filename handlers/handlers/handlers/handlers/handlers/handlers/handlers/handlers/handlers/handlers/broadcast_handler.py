# handlers/broadcast_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from config import OWNER_IDS
from database import Database

db = Database()

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ ပို့ချင်တဲ့စာ/ပုံ/video ကို reply ထောက်ပြီး `/bcast` လို့ရေးပါရှင့်")
        return
    
    reply_msg = update.message.reply_to_message
    groups = db.get_broadcast_groups()
    privates = db.get_broadcast_private()
    
    if not groups and not privates:
        await update.message.reply_text("❌ Broadcast list ထဲမှာ ဘာမှမရှိသေးပါ")
        return
    
    status_msg = await update.message.reply_text(
        f"📤 **Broadcast စတင်နေပါပြီ**\n\n"
        f"• Groups: {len(groups)} ခု\n"
        f"• Private: {len(privates)} ခု\n\n"
        f"⏳ ကျေးဇူးပြု၍ စောင့်ဆိုင်းပေးပါ..."
    )
    
    success_groups = 0
    failed_groups = []
    success_private = 0
    failed_private = []
    
    for group_id, group_name, group_link in groups:
        try:
            await send_media_message(context, group_id, reply_msg)
            success_groups += 1
        except Exception as e:
            failed_groups.append({"id": group_id, "reason": str(e)[:50]})
    
    for user_id, chat_id in privates:
        try:
            await send_media_message(context, chat_id, reply_msg)
            success_private += 1
        except Exception as e:
            failed_private.append({"id": user_id, "reason": str(e)[:50]})
    
    result_text = f"""📊 **Broadcast ရလဒ်**

📢 **Groups:**
• စုစုပေါင်း: {len(groups)} ခု
• ✅ ရောက်ရှိ: {success_groups} ခု
• ❌ မရောက်ရှိ: {len(failed_groups)} ခု

👤 **Private Chats:**
• စုစုပေါင်း: {len(privates)} ခု
• ✅ ရောက်ရှိ: {success_private} ခု
• ❌ မရောက်ရှိ: {len(failed_private)} ခု
"""
    
    if failed_groups:
        result_text += f"\n\n❌ **မရောက်ရှိသော Groups:**\n"
        for fail in failed_groups[:5]:
            result_text += f"• `{fail['id']}` - {fail['reason']}\n"
    
    if failed_private:
        result_text += f"\n\n❌ **မရောက်ရှိသော Private:**\n"
        for fail in failed_private[:5]:
            result_text += f"• `{fail['id']}` - {fail['reason']}\n"
    
    result_text += f"\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    await status_msg.edit_text(result_text)

async def send_media_message(context, chat_id, reply_msg):
    if reply_msg.text:
        await context.bot.send_message(chat_id=chat_id, text=reply_msg.text)
    elif reply_msg.photo:
        await context.bot.send_photo(chat_id=chat_id, photo=reply_msg.photo[-1].file_id, caption=reply_msg.caption or "")
    elif reply_msg.video:
        await context.bot.send_video(chat_id=chat_id, video=reply_msg.video.file_id, caption=reply_msg.caption or "")
    elif reply_msg.sticker:
        await context.bot.send_sticker(chat_id=chat_id, sticker=reply_msg.sticker.file_id)
    elif reply_msg.document:
        await context.bot.send_document(chat_id=chat_id, document=reply_msg.document.file_id, caption=reply_msg.caption or "")
    elif reply_msg.audio:
        await context.bot.send_audio(chat_id=chat_id, audio=reply_msg.audio.file_id, caption=reply_msg.caption or "")
    elif reply_msg.voice:
        await context.bot.send_voice(chat_id=chat_id, voice=reply_msg.voice.file_id)
    elif reply_msg.animation:
        await context.bot.send_animation(chat_id=chat_id, animation=reply_msg.animation.file_id, caption=reply_msg.caption or "")

async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or f"Group {chat_id}"
    chat_link = f"https://t.me/+{chat_id}"
    
    db.add_broadcast_group(chat_id, chat_title, chat_link)
    await update.message.reply_text(f"✅ Group `{chat_title}` ကို broadcast list ထဲထည့်ပြီးပါပြီ")

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not context.args:
        await update.message.reply_text("❌ `/removegroup [group_id]` လို့ရေးပါ")
        return
    
    try:
        group_id = int(context.args[0])
        db.remove_broadcast_group(group_id)
        await update.message.reply_text(f"✅ Group `{group_id}` ကို ဖျက်ပြီးပါပြီ")
    except ValueError:
        await update.message.reply_text("❌ Group ID ကို နံပါတ်အတိအကျထည့်ပါ")

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    groups = db.get_broadcast_groups()
    if not groups:
        await update.message.reply_text("📋 Broadcast list ထဲမှာ Group မရှိသေးပါ")
        return
    
    text = "📋 **Broadcast Groups:**\n\n"
    for i, (group_id, name, link) in enumerate(groups, 1):
        text += f"{i}. 📁 {name}\n   🆔 `{group_id}`\n\n"
    
    await update.message.reply_text(text[:4000])
