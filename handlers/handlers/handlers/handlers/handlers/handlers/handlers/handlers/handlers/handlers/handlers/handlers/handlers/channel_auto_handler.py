# handlers/channel_auto_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from config import OWNER_IDS, CHANNEL_ID
from database import Database

db = Database()

async def channel_auto_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id != CHANNEL_ID:
        return
    
    message = update.channel_post
    if not message:
        return
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📢 **Channel Auto Forward စတင်နေပါပြီ**\n\n"
                 "Groups နဲ့ Private Chats အကုန်လုံးကို ပို့ဆောင်နေပါပြီ..."
        )
    except:
        pass
    
    groups = db.get_broadcast_groups()
    privates = db.get_broadcast_private()
    
    total_groups = len(groups)
    total_private = len(privates)
    success_groups = 0
    failed_groups = []
    success_private = 0
    failed_private = []
    
    for group_id, group_name, group_link in groups:
        try:
            await send_media_message(context, group_id, message)
            success_groups += 1
        except Exception as e:
            error_msg = str(e)
            if "Forbidden" in error_msg or "bot was kicked" in error_msg:
                reason = "Bot ကို Group ထဲကဖယ်ထားပြီ"
            elif "Chat not found" in error_msg:
                reason = "Group မရှိတော့ပါ"
            elif "bot is not a member" in error_msg:
                reason = "Bot က Group ထဲမပါဝင်ပါ"
            else:
                reason = error_msg[:50]
            
            failed_groups.append({
                "id": group_id,
                "name": group_name,
                "reason": reason
            })
    
    for user_id, chat_id in privates:
        try:
            await send_media_message(context, chat_id, message)
            success_private += 1
        except Exception as e:
            error_msg = str(e)
            if "bot was blocked" in error_msg:
                reason = "User က Bot ကိုပိတ်ထားပြီ"
            elif "user is deactivated" in error_msg:
                reason = "User အကောင့်ပိတ်ထားပြီ"
            else:
                reason = error_msg[:50]
            
            failed_private.append({
                "id": user_id,
                "reason": reason
            })
    
    result_text = f"""📊 **Channel Auto Forward ရလဒ်**

📢 **Groups:**
• စုစုပေါင်း: {total_groups} ခု
• ✅ ရောက်ရှိ: {success_groups} ခု
• ❌ မရောက်ရှိ: {len(failed_groups)} ခု

👤 **Private Chats:**
• စုစုပေါင်း: {total_private} ခု
• ✅ ရောက်ရှိ: {success_private} ခု
• ❌ မရောက်ရှိ: {len(failed_private)} ခု
"""
    
    if failed_groups:
        result_text += f"\n\n❌ **မရောက်ရှိသော Groups ({len(failed_groups)}):**\n"
        for fail in failed_groups[:5]:
            result_text += f"• {fail['name']} - {fail['reason']}\n"
        if len(failed_groups) > 5:
            result_text += f"\n... နှင့် နောက်ထပ် {len(failed_groups) - 5} ခု"
    
    if failed_private:
        result_text += f"\n\n❌ **မရောက်ရှိသော Private Chats ({len(failed_private)}):**\n"
        for fail in failed_private[:5]:
            result_text += f"• ID: `{fail['id']}` - {fail['reason']}\n"
        if len(failed_private) > 5:
            result_text += f"\n... နှင့် နောက်ထပ် {len(failed_private) - 5} ခု"
    
    result_text += f"\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=result_text
        )
    except:
        pass
    
    for owner_id in OWNER_IDS:
        try:
            await context.bot.send_message(
                owner_id,
                f"📢 **Channel Auto Forward**\n\n"
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"✅ ရောက်ရှိ: {success_groups + success_private} ခု\n"
                f"❌ မရောက်ရှိ: {len(failed_groups) + len(failed_private)} ခု"
            )
        except:
            pass

async def send_media_message(context, chat_id, message):
    try:
        if message.text:
            await context.bot.send_message(chat_id=chat_id, text=message.text)
        elif message.photo:
            await context.bot.send_photo(chat_id=chat_id, photo=message.photo[-1].file_id, caption=message.caption or "")
        elif message.video:
            await context.bot.send_video(chat_id=chat_id, video=message.video.file_id, caption=message.caption or "")
        elif message.sticker:
            await context.bot.send_sticker(chat_id=chat_id, sticker=message.sticker.file_id)
        elif message.document:
            await context.bot.send_document(chat_id=chat_id, document=message.document.file_id, caption=message.caption or "")
        elif message.audio:
            await context.bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, caption=message.caption or "")
        elif message.voice:
            await context.bot.send_voice(chat_id=chat_id, voice=message.voice.file_id)
        elif message.animation:
            await context.bot.send_animation(chat_id=chat_id, animation=message.animation.file_id, caption=message.caption or "")
        elif message.video_note:
            await context.bot.send_video_note(chat_id=chat_id, video_note=message.video_note.file_id)
        elif message.poll:
            await context.bot.send_poll(chat_id=chat_id, question=message.poll.question, options=[option.text for option in message.poll.options])
    except Exception as e:
        raise e
