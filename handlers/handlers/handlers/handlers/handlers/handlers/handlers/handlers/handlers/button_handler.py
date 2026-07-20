# handlers/button_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📢 Support", url="https://t.me/BOTUAPTE"),
            InlineKeyboardButton("👤 Owner", url="https://t.me/Tear808")
        ],
        [
            InlineKeyboardButton("📞 Call System", callback_data="call_menu"),
            InlineKeyboardButton("👥 Admin List", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton("📋 My Groups", callback_data="my_groups"),
            InlineKeyboardButton("➕ Add to Group", url="https://t.me/Group_ai_help_bot?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 Ad System", callback_data="ad_info"),
            InlineKeyboardButton("❓ Help", callback_data="help_system")
        ],
        [
            InlineKeyboardButton("⏭ နောက်ထပ် ➡️", callback_data="more_buttons")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def more_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🤖 AI Chat", callback_data="ai_info"),
            InlineKeyboardButton("📚 Teach System", callback_data="teach_info")
        ],
        [
            InlineKeyboardButton("📜 Rule System", callback_data="rule_info"),
            InlineKeyboardButton("👋 Welcome System", callback_data="welcome_info")
        ],
        [
            InlineKeyboardButton("🛡️ Anti-Spam", callback_data="antispam_info"),
            InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_info")
        ],
        [
            InlineKeyboardButton("🔑 Ad Code System", callback_data="adcode_info"),
            InlineKeyboardButton("👑 Admin Commands", callback_data="admin_commands")
        ],
        [
            InlineKeyboardButton("⬅️ နောက်သို့", callback_data="back_to_start"),
            InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def help_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📚 **AI Group Helper Bot - အသုံးပြုပုံလမ်းညွှန်**

━━━━━━━━━━━━━━━━━━━━━━
🤖 **AI Chat System**
📌 **အသုံးပြုပုံ:**
• Group: `/ai [မေးခွန်း]`
• Private: စာရိုက်ရုံနဲ့ AI ဖြေမယ်

━━━━━━━━━━━━━━━━━━━━━━
👋 **Welcome System**
📌 **အသုံးပြုပုံ:**
• Admin/Owner သာ သုံးနိုင်မယ်
• `/setwelcome` - Video သတ်မှတ် (Reply ထောက်ပြီး)
• `/shortstory စာ` - စာသတ်မှတ်
• `/deletevideo` - Video ဖျက်
• `/deleteshortstory` - စာဖျက်

━━━━━━━━━━━━━━━━━━━━━━
📜 **Rule System**
📌 **အသုံးပြုပုံ:**
• `/setrule` - စည်းကမ်းသတ်မှတ် (Reply ထောက်ပြီး)
• `/gprue` - စည်းကမ်းကြည့်
• `/deaterue` - စည်းကမ်းဖျက်

━━━━━━━━━━━━━━━━━━━━━━
📚 **Teach System**
📌 **အသုံးပြုပုံ:**
• `/teach [အဖြေ]` - စာသင်ပေး (Reply ထောက်ပြီး)
• `/q` - မေးခွန်းသိမ်း
• `/a` - အဖြေသိမ်း
• `/teacher` - စာသင်ပုံလမ်းညွှန်

━━━━━━━━━━━━━━━━━━━━━━
📞 **Call System (@all)**
📌 **အသုံးပြုပုံ:**
• `/call [စာ]` - အားလုံးကိုခေါ်
• `/callsetting` - Settings ချိန်ညှိ

━━━━━━━━━━━━━━━━━━━━━━
🛡️ **Anti-Spam System**
📌 **အသုံးပြုပုံ:**
• ၁ခါ: သတိပေး
• ၂ခါ: သတိပေးပြီး စာဖျက်
• ၃ခါ: ၃မိနစ် Mute

━━━━━━━━━━━━━━━━━━━━━━
👑 **Admin System**
📌 **အသုံးပြုပုံ:**
• `/ban` - User ကို Ban (Reply ထောက်ပြီး)
• `/mute` - User ကို ၃မိနစ် Mute
• `/unmute` - User ကို Unmute

━━━━━━━━━━━━━━━━━━━━━━
📋 **Group List System**
📌 **အသုံးပြုပုံ:**
• "My Groups" ခလုပ်နှိပ်ပါ
• တစ်မျက်နှာ ၈ခုစီပြမယ်

━━━━━━━━━━━━━━━━━━━━━━
📢 **Ad Code System**
📌 **အသုံးပြုပုံ:**
• Owner: `/timebc 1h/6h/24h`
• User: `[ကုဒ်] [ကြော်ငြာစာ]`

━━━━━━━━━━━━━━━━━━━━━━
📝 **အခြား Command များ:**
• `/start` - Bot ကိုစတင်မယ်
• `/help` - ဒီစာကိုပြမယ်
• `/mygroups` - Group စာရင်းကြည့်

📢 **Channel:** @BOTUAPTE
👤 **Owner:** @Tear808"""

    if update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    welcome_text = """👋 မဂ်လာပါ!

🤖 ကျွန်တော်က **AI Group Helper Bot** ပါ။

📚 **အသုံးပြုနည်း:**
• Group: `/ai [မေးခွန်း]`
• Private: စာရိုက်ရုံနဲ့ AI ဖြေမယ်

👤 **Owner:** @Tear808
📢 **Channel:** @BOTUAPTE

ဘာမေးချင်လဲ ရေးပါ..."""
    
    keyboard = await start_buttons(update, context)
    await query.edit_message_text(welcome_text, reply_markup=keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "more_buttons":
        keyboard = await more_buttons(update, context)
        await query.edit_message_text(
            "📋 **နောက်ထပ် ဆက်တင်များ**\n\n"
            "အောက်ပါ စနစ်များအကြောင်း ပိုမိုသိရှိနိုင်ပါတယ်။",
            reply_markup=keyboard
        )
    
    elif data == "back_to_start":
        await back_to_start(update, context)
    
    elif data == "help_system":
        await help_system(update, context)
    
    elif data == "my_groups":
        from .group_list_handler import my_groups
        await my_groups(update, context)
    
    elif data == "call_menu":
        from .call_handler import call_settings
        await call_settings(update, context)
    
    elif data == "ad_info":
        text = """📢 **ကြော်ငြာစနစ်**

🔑 **ကုဒ်ဖြင့် ကြော်ငြာခြင်း**

📌 **Owner အတွက်:**
▪️ `/timebc 1h` - ၁နာရီ ကုဒ်
▪️ `/timebc 6h` - ၆နာရီ ကုဒ်
▪️ `/timebc 24h` - ၂၄နာရီ ကုဒ်
▪️ `/timetear` - ကုဒ်စာရင်း

📌 **အသုံးပြုသူအတွက်:**
▪️ ကုဒ်ရယူပါ
▪️ `[ကုဒ်] [ကြော်ငြာစာ]` လို့ပို့ပါ"""
        await query.edit_message_text(text)
    
    elif data == "bot_info":
        info_text = """🤖 **Bot Information**

📌 **Name:** Group AI Helper Bot
📦 **Version:** 3.0.0

⚡ **စနစ်များ:**
1️⃣ AI Chat System
2️⃣ Welcome System
3️⃣ Rule System
4️⃣ Teach System
5️⃣ Call System (@all)
6️⃣ Anti-Spam System
7️⃣ Button System
8️⃣ Admin System
9️⃣ Group List System
🔟 Ad Code System
1️⃣1️⃣ Bot Manager System

👤 **Owner:** @Tear808
📢 **Channel:** @BOTUAPTE"""
        await query.edit_message_text(info_text)
    
    elif data == "admin_list":
        await query.edit_message_text(
            "👥 **Admin List**\n\n"
            "Admin စာရင်းကို Welcome Message အောက်က\n"
            "`Admin ကြည့်ရန်` ခလုပ်နဲ့ ကြည့်ပါ။\n\n"
            "Group ထဲမှာပဲ ကြည့်လို့ရပါတယ်။"
        )
    
    # System Info Buttons
    elif data == "ai_info":
        await query.edit_message_text("🤖 **AI Chat System**\n\nGroup: `/ai [မေးခွန်း]`\nPrivate: စာရိုက်ရုံနဲ့ AI ဖြေမယ်")
    
    elif data == "teach_info":
        await query.edit_message_text("📚 **Teach System**\n\n`/teach [အဖြေ]` - စာသင်ပေး\n`/q` - မေးခွန်းသိမ်း\n`/a` - အဖြေသိမ်း")
    
    elif data == "rule_info":
        await query.edit_message_text("📜 **Rule System**\n\n`/setrule` - စည်းကမ်းသတ်မှတ်\n`/gprue` - စည်းကမ်းကြည့်\n`/deaterue` - စည်းကမ်းဖျက်")
    
    elif data == "welcome_info":
        await query.edit_message_text("👋 **Welcome System**\n\n`/setwelcome` - Video သတ်မှတ်\n`/shortstory စာ` - စာသတ်မှတ်\n`/deletevideo` - Video ဖျက်\n`/deleteshortstory` - စာဖျက်")
    
    elif data == "antispam_info":
        await query.edit_message_text("🛡️ **Anti-Spam System**\n\n၁ခါ: သတိပေး\n၂ခါ: သတိပေးပြီး စာဖျက်\n၃ခါ: ၃မိနစ် Mute")
    
    elif data == "broadcast_info":
        await query.edit_message_text("📢 **Broadcast System**\n\nOwner သာ သုံးနိုင်မယ်\nစာ/ပုံ/video ကို Reply ထောက်ပြီး `/bcast`")
    
    elif data == "adcode_info":
        await query.edit_message_text("🔑 **Ad Code System**\n\nOwner: `/timebc 1h/6h/24h`\nUser: `[ကုဒ်] [ကြော်ငြာစာ]`")
    
    elif data == "admin_commands":
        await query.edit_message_text("👑 **Admin Commands**\n\n`/ban` - User ကို Ban\n`/mute` - User ကို ၃မိနစ် Mute\n`/unmute` - User ကို Unmute")
