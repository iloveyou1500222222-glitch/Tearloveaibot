# handlers/group_list_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_IDS, GROUP_PAGE_SIZE
from database import Database

db = Database()

async def my_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message or update.callback_query.message
    
    all_groups = db.get_broadcast_groups()
    
    if not all_groups:
        text = "📋 **Group မရှိသေးပါ**\n\nBot ကို Group ထဲထည့်ပြီး `/addgroup` နဲ့ ထည့်ပါ။"
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await message.reply_text(text)
        return
    
    admin_groups = []
    for group_id, group_name, group_link in all_groups:
        try:
            admins = await context.bot.get_chat_administrators(group_id)
            for admin in admins:
                if admin.user.id == user_id:
                    admin_groups.append({
                        "id": group_id,
                        "name": group_name or f"Group {group_id}",
                        "link": group_link or f"https://t.me/+{group_id}"
                    })
                    break
        except:
            pass
    
    if not admin_groups:
        text = "📋 **သင် Admin ဖြစ်တဲ့ Group မရှိပါဘူး**"
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await message.reply_text(text)
        return
    
    total_groups = len(admin_groups)
    total_pages = (total_groups + GROUP_PAGE_SIZE - 1) // GROUP_PAGE_SIZE
    
    current_page = context.user_data.get('group_page', 0)
    if current_page >= total_pages:
        current_page = total_pages - 1
    if current_page < 0:
        current_page = 0
    
    context.user_data['group_page'] = current_page
    context.user_data['admin_groups'] = admin_groups
    
    start_idx = current_page * GROUP_PAGE_SIZE
    end_idx = min(start_idx + GROUP_PAGE_SIZE, total_groups)
    page_groups = admin_groups[start_idx:end_idx]
    
    keyboard = []
    
    for group in page_groups:
        button_text = f"📁 {group['name'][:20]}"
        keyboard.append([InlineKeyboardButton(button_text, url=group['link'])])
    
    nav_buttons = []
    
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Back", callback_data=f"group_page_{current_page - 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton("◀️ Back", callback_data="group_page_none"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {current_page + 1}/{total_pages}", callback_data="group_page_info"))
    
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"group_page_{current_page + 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="group_page_none"))
    
    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"📋 **သင် Admin ဖြစ်တဲ့ Groups ({total_groups})**\n\n"
    text += f"📄 စာမျက်နှာ {current_page + 1}/{total_pages}\n"
    text += f"📌 {start_idx + 1} - {end_idx} / {total_groups}\n\n"
    text += "Group တစ်ခုကိုနှိပ်ပြီး ဝင်ရောက်ပါ။"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await message.reply_text(text, reply_markup=reply_markup)

async def group_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "group_page_none":
        await query.answer("ဒီစာမျက်နှာမှာ နောက်ထပ် Group မရှိပါ")
        return
    
    if data == "group_page_info":
        await query.answer(f"စာမျက်နှာ {context.user_data.get('group_page', 0) + 1}")
        return
    
    if data.startswith("group_page_"):
        page = int(data.replace("group_page_", ""))
        context.user_data['group_page'] = page
        await my_groups(update, context)
