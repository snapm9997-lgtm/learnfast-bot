from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# МЕНЯЕМ МОДЕЛЬ НА СТАБИЛЬНУЮ Llama 4
MODEL = "meta-llama/llama-4-maverick:free"

# Здесь будет URL твоего будущего Mini App
# Пока оставим заглушку, но ссылка уже есть
MINI_APP_URL = "https://learnfast-bot.vercel.app/miniapp"

chat_histories = {}

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Bot is running! Use /app to open Mini App."
    
    if request.is_json:
        update = request.get_json()
        
        if 'message' in update:
            chat_id = str(update['message']['chat']['id'])
            user_text = update['message'].get('text', '')
            
            if user_text == '/start':
                keyboard = {
                    "inline_keyboard": [[{
                        "text": "🚀 Открыть приложение LearnFast",
                        "web_app": {"url": MINI_APP_URL}
                    }]]
                }
                send_message(chat_id, "Привет! Я — твой ИИ-помощник для бизнеса. Нажми на кнопку ниже, чтобы открыть приложение и начать работу.", reply_markup=keyboard)
                return jsonify({"status": "ok"})
            
            if user_text == '/app':
                keyboard = {
                    "inline_keyboard": [[{
                        "text": "🚀 Открыть приложение",
                        "web_app": {"url": MINI_APP_URL}
                    }]]
                }
                send_message(chat_id, "Открыть приложение:", reply_markup=keyboard)
                return jsonify({"status": "ok"})
            
            # Обработка сообщений из чата с ботом (пока оставим)
            if user_text == '/clear':
                if chat_id in chat_histories:
                    del chat_histories[chat_id]
                send_message(chat_id, "🧹 История диалога очищена!")
                return jsonify({"status": "ok"})
            
            # ... здесь остальная логика для ответов в чате ...
            # (оставлю как было, но основной фокус на Mini App)
            
    return jsonify({"status": "ok"})

def ask_model(messages):
    system_prompt = {
        "role": "system",
        "content": "Ты — профессиональный ИИ-ассистент для бизнеса. Твоя задача: помогать с маркетингом, продажами, написанием писем, генерацией идей для контента. Отвечай четко, по делу и предлагай готовые решения."
    }
    full_messages = [system_prompt] + messages
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": full_messages, "temperature": 0.7, "max_tokens": 2000},
        timeout=60
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"Ошибка {response.status_code}: {response.text}")

def send_message(chat_id, text, reply_markup=None):
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                requests.post(f"{URL}/sendMessage", json={**payload, "text": text[i:i+4000]})
        else:
            requests.post(f"{URL}/sendMessage", json=payload)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    app.run()
