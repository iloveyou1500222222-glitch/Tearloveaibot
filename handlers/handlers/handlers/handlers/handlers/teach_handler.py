# handlers/teach_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import Database
from config import OWNER_IDS

db = Database()

async def teach_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ စာ/စတစ်ကာကို reply ထောက်ပြီး `/teach [အဖြေ]` ရေးပါ")
        return
    
    question = update.message.reply_to_message.text or "sticker"
    answer = " ".join(context.args) if context.args else ""
    
    if not answer:
        await update.message.reply_text("❌ `/teach [အဖြေ]` လို့ရေးပါ")
        return
    
    forbidden_words = ["sex", "fuck", "ရိုင်း", "ညစ်", "ကာမ", "လိင်"]
    if any(word in answer.lower() for word in forbidden_words) or any(word in question.lower() for word in forbidden_words):
        await update.message.reply_text("❌ မသင်ပေးနိုင်ပါ။ သင့်လျော်သောစာသား ဖြစ်ပါစေ။")
        return
    
    db.save_teach(question, answer, chat_id)
    await update.message.reply_text("✅ မှတ်သားလိုက်ပါပြီရှင့်")
    
    for owner_id in OWNER_IDS:
        try:
            await context.bot.send_message(
                owner_id,
                f"📚 **စာသင်ထားခြင်း**\n\n"
                f"❓ မေးခွန်း: {question}\n"
                f"💬 အဖြေ: {answer}\n"
                f"👤 သင်ပေးသူ: {update.effective_user.full_name}\n"
                f"🆔 {update.effective_user.id}\n"
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except:
            pass

async def q_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ မေးခွန်းကို reply ထောက်ပြီး `/q` ရေးပါ")
        return
    
    context.user_data['teach_question'] = update.message.reply_to_message.text or "sticker"
    await update.message.reply_text("✅ မေးခွန်းသိမ်းထားပါပြီ။ အဖြေကို reply ထောက်ပြီး `/a` ရေးပါ")

async def a_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ အဖြေကို reply ထောက်ပြီး `/a` ရေးပါ")
        return
    
    question = context.user_data.get('teach_question')
    if not question:
        await update.message.reply_text("❌ မေးခွန်းမရှိသေးပါ။ `/q` နဲ့ အရင်သတ်မှတ်ပါ")
        return
    
    answer = update.message.reply_to_message.text or "sticker"
    
    forbidden_words = ["sex", "fuck", "ရိုင်း", "ညစ်"]
    if any(word in answer.lower() for word in forbidden_words):
        await update.message.reply_text("❌ မသင်ပေးနိုင်ပါ")
        return
    
    db.save_teach(question, answer, chat_id)
    await update.message.reply_text("✅ မှတ်သားလိုက်ပါပြီရှင့်")
    context.user_data['teach_question'] = None

async def teacher_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """📚 **မဂ်လာပါရှင့် စာသင်ချင်းလမ်းညွှန်** 📣📣

**Ver1.1** မေးခွန်းအဖြစ် စတစ်ကာ(သို့)စာကို
Reply ထောက်ပြီး `/teach [အဖြေ]` လို့ရေးပေးပါရှင့်

**Ver1.2** မေးခွန်းအဖြစ် စတစ်ကာ(သို့)စာကို
Reply ထောက်ပြီး `/q` လို့ပို့ပေးပါရှင့်
ပီးနောက် အဖြေကို Reply ထောက်ပြီး `/a` လို့ပို့ပေးပါရှင့်

"မှတ်သားထားလိုက်ပါပီရှင့်" ဆိုရင် အောင်မြင်ပါပီ။

💡 ကြောညာအတွက်: @Tear808"""
    
    await update.message.reply_text(help_text)
