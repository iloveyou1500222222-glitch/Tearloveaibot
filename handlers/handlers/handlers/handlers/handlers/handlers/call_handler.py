# handlers/call_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
import random
from datetime import datetime
from database import Database
from config import OWNER_IDS

db = Database()

CALL_EMOJIS = [
    "😀", "😬", "😁", "😂", "😃", "😄", "😅", "😇", "😉", "😊",
    "🙂", "🙃", "☺", "😋", "😌", "😍", "🥰", "😘", "😗", "😙",
    "😚", "😜", "🤣", "🥳", "🤩", "😎", "🤓", "🤑", "😛", "🤪",
    "😝", "🤗", "🤭", "🤫", "😏", "😶", "😐", "😑", "😒", "🤨",
    "🙄", "🤔", "🧐", "😳", "🥺", "🤤", "🤥", "😕", "😔", "🤯",
    "🤬", "😡", "😠", "😟", "😞", "🤧", "🙁", "☹", "😣", "😖",
    "😫", "😩", "😤", "😮", "😱", "😨", "😥", "😪", "😓", "😭",
    "😵", "😲", "🤐", "😷", "👿", "😈", "💩", "💤", "🥱", "😴",
    "🤕", "🤒", "🤢", "🤮", "🥴", "🥵", "🥶", "🤠", "👹", "🤡",
    "👺", "💀", "☠", "👻", "👽", "🤖", "👾", "😺", "😾", "😿",
    "🙀", "😽", "😼", "😻", "😹", "😸", "👏", "👋", "👍", "👎",
    "👊", "✊", "✌", "🖖", "🤚", "✋", "🤏", "👌", "🤞", "🤛",
    "🤜", "👐", "🤲", "🤝", "💪", "🙏", "☝", "🤌", "👆", "🤘",
    "🤙", "🤟", "🖐", "🖕", "👉", "👈", "👇", "🦾", "🦿", "🦵",
    "🦶", "✍", "💅", "🤳", "👄", "👀", "👁", "🧠", "👃", "🦻",
    "👂", "👅", "🦷", "👤", "👥", "🗣", "👶", "👦", "👧", "👨🏻",
    "🧔", "👩🏿", "👩🏾", "👩🏽", "👩🏼", "👩🏻", "👨🏾", "👨🏽", "👨🏼", "🤵",
    "👼", "🤴", "👸", "👰", "🎅", "🤶", "👷", "🐶", "🐱", "🐭",
    "🐹", "🐰", "🐻", "🐼", "🐨", "🐵", "🐙", "🐸", "🐽", "🐷",
    "🐮", "🦁", "🐯", "🙈", "🙉", "🙊", "🐒", "🐔", "🐧", "🐦",
    "🐤", "🦇", "🦄", "🐴", "🐗", "🦊", "🐺", "🐥", "🐣", "🐝",
    "🦋", "🐛", "🐌", "🐞", "🐜", "🕷", "🦗", "🐟", "🐠", "🐢",
    "🐍", "🦎", "🦀", "🦂", "🦟", "🍏", "🍎", "🍐", "🍊", "🥭",
    "🥥", "🧅", "🥦", "🍆", "🍈", "🍖", "🧈", "🍞", "🏀", "🏈",
    "🎾", "🏉", "🏸", "🏹", "🪁", "🥌", "🕴", "🚒", "🚐", "🦼",
    "🛴", "🚝", "🚆", "🖲", "☎", "📡", "💴", "🩸", "😯", "😦", "😧"
]

LANGUAGES = {
    "🇲🇲": "Myanmar", "🇯🇵": "Japanese", "🇮🇳": "Hindi",
    "🇵🇰": "Urdu", "🇰🇭": "Khmer", "🇰🇵": "Korean",
    "🇱🇨": "Chinese", "🇱🇮": "Lao", "🇱🇰": "Sinhala",
    "🇱🇷": "Liberia", "🇱🇸": "Lesotho", "🇱🇹": "Lithuanian",
    "🇱🇺": "Luxembourgish", "🇱🇻": "Latvian", "🇲🇰": "Macedonian",
    "🇲🇱": "Malian", "🇲🇳": "Mongolian", "🇲🇴": "Macanese",
    "🇲🇵": "Northern Mariana", "🇲🇷": "Mauritanian", "🇲🇿": "Mozambique",
    "🇲🇽": "Spanish", "🇲🇼": "Malawi", "🇲🇻": "Dhivehi",
    "🇲🇺": "Mauritian", "🇲🇹": "Maltese", "🇲🇸": "Montserrat",
    "🇳🇦": "Namibian", "🇳🇮": "Nicaraguan", "🇳🇱": "Dutch",
    "🇳🇴": "Norwegian", "🇵🇫": "French Polynesian", "🇵🇪": "Peruvian",
    "🇵🇦": "Panamanian", "🇴🇲": "Omani", "🇳🇿": "New Zealand",
    "🇳🇺": "Niuean", "🇳🇷": "Nauruan", "🇦🇩": "Andorran", "🇨🇳": "Chinese"
}

async def call_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    message = update.message
    
    settings = db.get_call_settings(chat_id)
    who_can_call = settings['who_can_call']
    
    if who_can_call == 'admin':
        if not (await is_admin(update, context)):
            await message.reply_text("❌ တောင်းပန်ပါတယ်ရှင့်... သင့်မှာခွင့်ပြုချက်မရှိပါ")
            return
    elif who_can_call == 'owner':
        if user.id not in OWNER_IDS:
            await message.reply_text("❌ တောင်းပန်ပါတယ်ရှင့်... သင့်မှာခွင့်ပြုချက်မရှိပါ")
            return
    
    call_text = " ".join(context.args) if context.args else "အားလုံးကိုခေါ်ဆိုပါတယ်"
    
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        members = []
        for admin in admins:
            if admin.user.username:
                members.append(admin.user)
    except:
        members = []
    
    if not members:
        await message.reply_text("❌ ခေါ်ဆိုရန် အဖွဲ့ဝင်မရှိပါ")
        return
    
    await message.reply_text(f"🔊 မဂ်လာပါရှင့် 0.2ms နဲစတင်ခေါ်ဆိုပေးနေပါပီရှင့်")
    
    emoji_list = []
    emoji_index = 0
    total_emojis = len(CALL_EMOJIS)
    
    for i in range(len(members)):
        emoji = CALL_EMOJIS[emoji_index % total_emojis]
        emoji_list.append(emoji)
        emoji_index += 1
    
    random.shuffle(emoji_list)
    
    sent_count = 0
    use_emoji = settings['use_emoji']
    call_count_per_message = settings['call_count']
    message_buffer = []
    
    for i, member in enumerate(members):
        if member.username:
            username = f"@{member.username}"
            emoji = emoji_list[i] if i < len(emoji_list) else random.choice(CALL_EMOJIS)
            
            if use_emoji:
                mention = f"{emoji} [{username}](tg://user?id={member.id})"
            else:
                mention = username
            
            message_buffer.append(mention)
            
            if len(message_buffer) >= call_count_per_message:
                full_text = "\n".join(message_buffer) + f"\n\n{call_text}"
                await context.bot.send_message(chat_id, full_text, parse_mode="Markdown")
                message_buffer = []
                await asyncio.sleep(0.2)
            
            sent_count += 1
    
    if message_buffer:
        full_text = "\n".join(message_buffer) + f"\n\n{call_text}"
        await context.bot.send_message(chat_id, full_text, parse_mode="Markdown")
    
    await context.bot.send_message(
        chat_id,
        f"\n━━━━━━━━━━━━━━━━\n👤 By @Tear808\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    await message.reply_text(f"✅ ခေါ်ဆိုမှုပြီးဆုံးပါပြီ။ လူ {sent_count} ယောက်ကိုခေါ်ဆိုခဲ့ပါတယ်")

async def call_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    settings = db.get_call_settings(chat_id)
    
    keyboard = [
        [InlineKeyboardButton(f"🌍 ဘာသာစကား ({settings['language']})", callback_data="call_lang")],
        [InlineKeyboardButton(f"👥 ခေါ်ဆိုလူဉီးရေ ({settings['call_count']})", callback_data="call_count")],
        [InlineKeyboardButton(f"🔑 ခေါ်ဆိုနိုင်သူ ({settings['who_can_call']})", callback_data="call_who")],
        [InlineKeyboardButton(f"🎭 Emoji / Link", callback_data="call_emoji")],
        [InlineKeyboardButton("❌ Delete", callback_data="call_delete")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text("⚙️ **Call Settings Menu**", reply_markup=reply_markup)
    else:
        await update.message.reply_text("⚙️ **Call Settings Menu**", reply_markup=reply_markup)

async def call_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = query.message.chat.id
    
    if data == "call_lang":
        keyboard = []
        row = []
        for i, (flag, name) in enumerate(LANGUAGES.items(), 1):
            row.append(InlineKeyboardButton(f"{flag} {name}", callback_data=f"lang_{flag}"))
            if i % 3 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="call_back")])
        await query.edit_message_text("🌍 ဘာသာစကားရွေးပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("lang_"):
        lang = data.replace("lang_", "")
        db.update_call_settings(chat_id, "language", lang)
        await query.edit_message_text(f"✅ ဘာသာစကား {LANGUAGES[lang]} သတ်မှတ်ပြီးပါပြီ")
    
    elif data == "call_count":
        keyboard = [
            [InlineKeyboardButton("👥 ၃ယောက်", callback_data="count_3")],
            [InlineKeyboardButton("👥 ၅ယောက်", callback_data="count_5")],
            [InlineKeyboardButton("👥 ၇ယောက်", callback_data="count_7")],
            [InlineKeyboardButton("🔙 Back", callback_data="call_back")]
        ]
        await query.edit_message_text("👥 ခေါ်ဆိုလူဉီးရေ ရွေးပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("count_"):
        count = int(data.replace("count_", ""))
        db.update_call_settings(chat_id, "call_count", count)
        await query.edit_message_text(f"✅ လူ {count} ယောက်သတ်မှတ်ပြီးပါပြီ")
    
    elif data == "call_who":
        keyboard = [
            [InlineKeyboardButton("👑 Admin", callback_data="who_admin")],
            [InlineKeyboardButton("👤 Owner", callback_data="who_owner")],
            [InlineKeyboardButton("👥 All", callback_data="who_all")],
            [InlineKeyboardButton("🔙 Back", callback_data="call_back")]
        ]
        await query.edit_message_text("🔑 ခေါ်ဆိုနိုင်သူ ရွေးပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("who_"):
        who = data.replace("who_", "")
        db.update_call_settings(chat_id, "who_can_call", who)
        await query.edit_message_text(f"✅ {who} သတ်မှတ်ပြီးပါပြီ")
    
    elif data == "call_emoji":
        settings = db.get_call_settings(chat_id)
        current = "Emoji" if settings['use_emoji'] else "Link"
        keyboard = [
            [InlineKeyboardButton(f"🎭 Emoji", callback_data="emoji_on")],
            [InlineKeyboardButton(f"🔗 Link", callback_data="emoji_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="call_back")]
        ]
        await query.edit_message_text(f"🎭 လက်ရှိ: {current}\n\nEmoji / Link ရွေးပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "emoji_on":
        db.update_call_settings(chat_id, "use_emoji", True)
        await query.edit_message_text("✅ Emoji mode သတ်မှတ်ပြီးပါပြီ")
    
    elif data == "emoji_off":
        db.update_call_settings(chat_id, "use_emoji", False)
        await query.edit_message_text("✅ Link mode သတ်မှတ်ပြီးပါပြီ")
    
    elif data == "call_delete":
        await query.edit_message_text("✅ Settings ဖျက်ပြီးပါပြီ")
    
    elif data == "call_back":
        await call_settings(update, context)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
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
