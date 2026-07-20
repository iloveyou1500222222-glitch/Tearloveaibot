# handlers/ai_handler.py
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from config import HF_TOKEN

HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

async def get_ai_response(prompt: str, is_group: bool = False) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }
        
        if is_group:
            system_prompt = """You are a helpful AI assistant. Keep responses VERY SHORT (max 2-3 sentences). Be playful and use emojis."""
        else:
            system_prompt = """You are a helpful AI assistant. Provide detailed, accurate responses."""
        
        full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{prompt}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                HF_API_URL,
                json={
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 150 if is_group else 500,
                        "temperature": 0.8 if is_group else 0.7
                    }
                },
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").replace(full_prompt, "").strip()[:4000]
                return "AI မှ အဖြေရယူ၍မရပါ။"
            return f"AI ဆာဗာအခြေအနေ: {response.status_code}"
    except Exception as e:
        return f"AI ချိတ်ဆက်မှုအမှား: {str(e)[:100]}"

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❌ `/ai [မေးခွန်း]` လို့ရေးပါရှင့်")
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await get_ai_response(prompt, is_group=True)
    await update.message.reply_text(reply)

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await get_ai_response(update.message.text, is_group=False)
    context.user_data['last_ai_reply'] = reply
    await update.message.reply_text(reply)
