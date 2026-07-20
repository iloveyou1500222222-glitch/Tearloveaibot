# handlers/broadcast_code_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import random
import string
from config import OWNER_IDS
from database import Database

db = Database()

async def create_broadcast_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ `/timebc [အချိန်]` လို့ရေးပါ\n\n"
            "📌 **ဥပမာ:**\n"
            "▪️ `/timebc 1h` - ၁နာရီ\n"
            "▪️ `/timebc 6h` - ၆နာရီ\n"
            "▪️ `/timebc 24h` - ၂၄နာရီ"
        )
        return
    
    time_str = context.args[0].lower()
    try:
        if time_str.endswith('h'):
            hours = int(time_str[:-1])
        else:
            hours = int(time_str)
        
        if hours <= 0 or hours > 24:
            await update.message.reply_text("❌ ၁နာရီကနေ ၂၄နာရီအတွင်း သတ်မှတ်ပါ")
            return
        
        expires_in = timedelta(hours=hours)
    except ValueError:
        await update.message.reply_text("❌ ပုံစံမှားပါတယ်။ ဥပမာ: `/timebc 1h`")
        return
    
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    created_at = datetime.now()
    expires_at = created_at + expires_in
    
    db.save_broadcast_code(code, user_id, expires_at)
    
    await update.message.reply_text(
        f"✅ **ကြော်ငြာကုဒ် ဖန်တီးပြီးပါပြီ**\n\n"
        f"🔑 **ကုဒ်:** `{code}`\n"
        f"⏰ **သက်တမ်း:** {hours} နာရီ\n"
        f"📅 **စတင်:** {created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"⏳ **ကုန်ဆုံး:** {expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"📝 သုံးသူက Bot ကို `{code} [ကြော်ငြာစာ]` လို့ပို့ရမှာပါ"
    )

async def use_broadcast_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message
    text = message.text
    
    if not text:
        return
    
    parts = text.split(' ', 1)
    if len(parts) < 2:
        return
    
    code = parts[0].strip().upper()
    ad_text = parts[1].strip()
    
    code_data = db.get_broadcast_code(code)
    
    if not code_data:
        await message.reply_text("❌ ကုဒ်မမှန်ပါ")
        return
    
    code_info = {
        "code": code_data[0],
        "owner_id": code_data[1],
        "created_at": datetime.fromisoformat(code_data[2]),
        "expires_at": datetime.fromisoformat(code_data[3]),
        "used_by": code_data[4],
        "used_at": code_data[5],
        "is_used": code_data[6] if len(code_data) > 6 else 0
    }
    
    if datetime.now() > code_info["expires_at"]:
        await message.reply_text("❌ ဤကုဒ်သည် သက်တမ်းကုန်သွားပါပြီ။")
        return
    
    if code_info["is_used"]:
        await message.reply_text("❌ ဤကုဒ်ကို အသုံးပြုပြီးပါပြီ။")
        return
    
    forbidden_words = ["sex", "fuck", "ရိုင်း", "ညစ်", "လိင်", "ပေါက်ကွဲ"]
    if any(word in ad_text.lower() for word in forbidden_words):
        await message.reply_text("❌ မသင့်လျော်သော စာသားပါဝင်နေပါတယ်။")
        return
    
    db.use_broadcast_code(code, user_id, ad_text)
    
    await message.reply_text(
        f"✅ **မဂ်လာပါရှင့်!**\n\n"
        f"🔑 ကုဒ်: `{code}`\n"
        f"⏰ ကျန်အချိန်: {code_info['expires_at'] - datetime.now()}\n\n"
        f"📢 သင့်ကြော်ငြာကို ပို့ဆောင်နေပါပြီ..."
    )
    
    groups = db.get_broadcast_groups()
    success_count = 0
    fail_count = 0
    failed_groups = []
    
    for group_id, group_name, group_link in groups:
        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=f"📢 **ကြော်ငြာ**\n\n{ad_text}\n\n━━━━━━━━━━━━━━━━\n👤 @{update.effective_user.username or 'User'}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            success_count += 1
        except Exception as e:
            fail_count += 1
            failed_groups.append({
                "id": group_id,
                "name": group_name,
                "reason": str(e)[:50]
            })
    
    result_text = f"✅ **ကြော်ငြာပို့ဆောင်ပြီးပါပြီ**\n\n"
    result_text += f"✅ ရောက်ရှိ: {success_count} ခု\n"
    result_text += f"❌ မရောက်ရှိ: {fail_count} ခု\n"
    
    if failed_groups:
        result_text += f"\n❌ **မရောက်ရှိသော Groups:**\n"
        for fail in failed_groups[:5]:
            result_text += f"• {fail['name']} - {fail['reason']}\n"
    
    result_text += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    await message.reply_text(result_text)

async def list_broadcast_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    results = db.get_all_broadcast_codes(limit=50)
    
    if not results:
        await update.message.reply_text("📋 ကြော်ငြာကုဒ်မရှိသေးပါ")
        return
    
    text = "📊 **ကြော်ငြာကုဒ်စာရင်း**\n\n"
    
    for i, row in enumerate(results, 1):
        code = row[0]
        created = datetime.fromisoformat(row[2]).strftime('%Y-%m-%d %H:%M')
        expires = datetime.fromisoformat(row[3]).strftime('%Y-%m-%d %H:%M')
        is_used = "✅ သုံးပြီး" if row[6] else "⏳ မသုံးရသေး"
        used_by = row[4] if row[4] else "-"
        message_text = row[7] if row[7] else "-"
        
        text += f"{i}. 🔑 `{code}`\n"
        text += f"   📅 {created} → {expires}\n"
        text += f"   📝 {is_used}"
        if row[6]:
            text += f" | 👤 {used_by}"
        text += "\n\n"
    
    await update.message.reply_text(text[:4000])
