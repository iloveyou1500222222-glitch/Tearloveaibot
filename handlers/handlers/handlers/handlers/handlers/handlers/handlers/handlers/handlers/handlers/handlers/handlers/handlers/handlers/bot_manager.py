# handlers/bot_manager.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import httpx
from config import OWNER_IDS
from database import Database

db = Database()

# ===== ၁။ BotSosar စနစ်ကိုစတင်ခြင်း =====

async def bot_sosar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    text = """🤖 **BotSosar - Multi Bot Management System**

📌 **အသုံးပြုပုံ:**

🔑 **Bot စာရင်းသွင်းခြင်း:**
`/botcoline [BOT_TOKEN]`

📋 **စာရင်းသွင်းထားတဲ့ Bot များ:**
`/botlist`

📊 **မှတ်တမ်းကြည့်ခြင်း:**
`/botdm`

🗑️ **Bot ဖျက်ခြင်း:**
`/botremove [BOT_ID]`

🔄 **Bot အခြေအနေစစ်ဆေးခြင်း:**
`/botcheck`

⚠️ **သတိပေးချက်:**
• Token များကို မလိုအပ်ပဲ တစ်ခြားသူမပေးပါနဲ့
• Owner များသာ သုံးနိုင်ပါတယ်

👤 **Owner:** @Tear808"""

    await update.message.reply_text(text)

# ===== ၂။ Bot Token စာရင်းသွင်းခြင်း =====

async def botcoline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ `/botcoline [BOT_TOKEN]` လို့ရေးပါရှင့်\n\n"
            "📌 ဥပမာ: `/botcoline 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`"
        )
        return
    
    token = context.args[0].strip()
    
    is_valid, bot_info = await check_bot_token(token)
    
    if not is_valid:
        await update.message.reply_text(
            "❌ **Token မမှန်ပါရှင့်**\n\n"
            "ကျေးဇူးပြု၍ Token အစစ်ယူထည့်ပေးပါရှင့်\n\n"
            "📌 @BotFather မှ ရယူပါ"
        )
        return
    
    existing = db.get_all_registered_bots()
    for bot in existing:
        if bot[0] == token:
            await update.message.reply_text(
                f"⚠️ ဤ Bot ကို စာရင်းသွင်းပြီးသားပါ\n\n"
                f"📛 {bot[1]}\n"
                f"🆔 {bot[3]}\n"
                f"📅 {bot[4]}"
            )
            return
    
    db.register_bot(
        token=token,
        bot_name=bot_info['name'],
        bot_username=bot_info['username'],
        bot_id=bot_info['id'],
        added_by=user_id
    )
    
    reply_text = f"""✅ **Bot စာရင်းသွင်းပြီးပါပြီရှင့်**

📛 **အမည်:** {bot_info['name']}
🆔 **ID:** {bot_info['id']}
📛 **Username:** @{bot_info['username']}
🔑 **Token:** `{token[:10]}...{token[-5:]}`
👤 **ထည့်သူ:** {update.effective_user.full_name}
📅 **အချိန်:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 ယခုမှစပြီး ဒီ Bot ကို စာရင်းထဲမှာ သိမ်းထားပါပြီ
"""
    
    await update.message.reply_text(reply_text)

async def check_bot_token(token: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return True, {
                        'id': data['result']['id'],
                        'name': data['result']['first_name'],
                        'username': data['result']['username']
                    }
    except:
        pass
    return False, None

# ===== ၃။ Bot စာရင်းကြည့်ခြင်း =====

async def botlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    bots = db.get_all_registered_bots()
    
    if not bots:
        await update.message.reply_text("📋 စာရင်းသွင်းထားတဲ့ Bot မရှိသေးပါ")
        return
    
    text = "🤖 **စာရင်းသွင်းထားတဲ့ Bot များ**\n\n"
    
    for i, bot in enumerate(bots, 1):
        token = bot[0]
        name = bot[1]
        username = bot[2]
        bot_id = bot[3]
        added_by = bot[4]
        added_at = datetime.fromisoformat(bot[5]).strftime('%Y-%m-%d %H:%M')
        is_active = "🟢 အလုပ်လုပ်နေ" if bot[6] else "🔴 ပိတ်ထားပြီ"
        
        text += f"{i}. 📛 {name}\n"
        text += f"   🆔 {bot_id}\n"
        text += f"   📛 @{username}\n"
        text += f"   🔑 `{token[:10]}...{token[-5:]}`\n"
        text += f"   📝 {is_active}\n"
        text += f"   👤 ထည့်သူ: {added_by}\n"
        text += f"   📅 {added_at}\n\n"
    
    await update.message.reply_text(text[:4000])

# ===== ၄။ မှတ်တမ်းကြည့်ခြင်း =====

async def botdm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    bots = db.get_all_registered_bots()
    
    if not bots:
        await update.message.reply_text("📋 စာရင်းသွင်းထားတဲ့ Bot မရှိသေးပါ")
        return
    
    text = "📊 **Bot စာရင်းသွင်းမှတ်တမ်း**\n\n"
    
    for i, bot in enumerate(bots, 1):
        name = bot[1]
        username = bot[2]
        bot_id = bot[3]
        added_by = bot[4]
        added_at = datetime.fromisoformat(bot[5]).strftime('%Y-%m-%d %H:%M')
        is_active = "🟢 အသက်ရှင်" if bot[6] else "🔴 ပိတ်ထားပြီ"
        
        text += f"{i}. 📛 {name} (@{username})\n"
        text += f"   🆔 {bot_id}\n"
        text += f"   📝 {is_active}\n"
        text += f"   👤 ထည့်သူ: {added_by}\n"
        text += f"   📅 {added_at}\n\n"
    
    await update.message.reply_text(text[:4000])

# ===== ၅။ Bot ဖျက်ခြင်း =====

async def botremove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ `/botremove [BOT_ID]` လို့ရေးပါ\n\n"
            "📌 ဥပမာ: `/botremove 123456789`"
        )
        return
    
    try:
        bot_id = int(context.args[0])
        bots = db.get_all_registered_bots()
        
        for bot in bots:
            if bot[3] == bot_id:
                db.remove_bot(bot[0])
                await update.message.reply_text(
                    f"✅ Bot `{bot[1]}` (@{bot[2]}) ကို စာရင်းထဲကဖျက်ပြီးပါပြီ"
                )
                return
        
        await update.message.reply_text(f"❌ Bot ID `{bot_id}` ကို မတွေ့ပါ")
    except ValueError:
        await update.message.reply_text("❌ Bot ID ကို နံပါတ်အတိအကျထည့်ပါ")

# ===== ၆။ Bot အခြေအနေစစ်ဆေးခြင်း =====

async def botcheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ ခွင့်ပြုချက်မရှိပါ")
        return
    
    bots = db.get_all_registered_bots()
    
    if not bots:
        await update.message.reply_text("📋 စာရင်းသွင်းထားတဲ့ Bot မရှိသေးပါ")
        return
    
    status_msg = await update.message.reply_text("🔄 Bot အခြေအနေများကို စစ်ဆေးနေပါပြီ...")
    
    text = "📊 **Bot အခြေအနေများ**\n\n"
    alive_count = 0
    dead_count = 0
    
    for bot in bots:
        token = bot[0]
        name = bot[1]
        username = bot[2]
        bot_id = bot[3]
        
        is_alive = await check_bot_alive(token)
        
        if is_alive:
            status = "🟢 အသက်ရှင်"
            alive_count += 1
            db.update_bot_status(token, 1)
        else:
            status = "🔴 ပိတ်ထားပြီ"
            dead_count += 1
            db.update_bot_status(token, 0)
        
        text += f"📛 {name} (@{username})\n"
        text += f"   🆔 {bot_id}\n"
        text += f"   📝 {status}\n\n"
    
    text += f"\n✅ အသက်ရှင်: {alive_count} ခု\n"
    text += f"❌ ပိတ်ထားပြီ: {dead_count} ခု\n"
    text += f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    await status_msg.edit_text(text)

async def check_bot_alive(token: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            return response.status_code == 200
    except:
        return False
