from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Настройки Telegram
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"

# Настройки OpenRouter
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Модель - автоматический выбор работающей
MODEL = "qwen/qwen-2.5-72b-instruct:free"

# Словарь для хранения истории диалогов
chat_histories = {}

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Bot is running with OpenRouter!"
    
    if request.is_json:
        update = request.get_json()
        
        if 'message' in update:
            chat_id = str(update['message']['chat']['id'])
            user_text = update['message'].get('text', '')
            
            # Пропускаем команды, но обрабатываем /clear отдельно
            if user_text == '/clear':
                if chat_id in chat_histories:
                    del chat_histories[chat_id]
                send_message(chat_id, "🧹 История диалога очищена!")
                return jsonify({"status": "ok"})
            
            if user_text.startswith('/'):
                send_message(chat_id, "Доступные команды: /clear - очистить историю")
                return jsonify({"status": "ok"})
            
            # Инициализируем историю для нового чата
            if chat_id not in chat_histories:
                chat_histories[chat_id] = []
            
            # Добавляем сообщение пользователя
            chat_histories[chat_id].append({"role": "user", "content": user_text})
            
            try:
                # Запрос к OpenRouter
                answer = ask_openrouter(chat_histories[chat_id])
                
                # Добавляем ответ в историю
                chat_histories[chat_id].append({"role": "assistant", "content": answer})
                
                # Ограничиваем историю последними 10 сообщениями
                if len(chat_histories[chat_id]) > 10:
                    chat_histories[chat_id] = chat_histories[chat_id][-10:]
                
                send_message(chat_id, answer)
                
            except Exception as e:
                send_message(chat_id, f"❌ Ошибка: {str(e)}")
    
    return jsonify({"status": "ok"})

def ask_openrouter(messages):
    """Отправляет запрос к OpenRouter"""
    
    system_prompt = {
        "role": "system",
        "content": """Ты — умный и дружелюбный ИИ-помощник для учёбы и работы.
Отвечай полезно, понятно и по делу. Помогай с учебой и работой."""
    }
    
    full_messages = [system_prompt] + messages
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": full_messages,
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"Ошибка {response.status_code}: {response.text}")

def send_message(chat_id, text):
    """Отправляет сообщение в Telegram"""
    try:
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                requests.post(f"{URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": text[i:i+4000]
                })
        else:
            requests.post(f"{URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": text
            })
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    app.run()
