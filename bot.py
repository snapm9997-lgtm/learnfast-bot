from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Настройки Telegram
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"

# Хранилище истории диалогов
chat_histories = {}

# URL для Puter.js AI Gateway (работает с Qwen)
PUTER_AI_URL = "https://ai.puter.com/api/v1/chat/completions"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Bot is running with Qwen (free via Puter.js)!"
    
    if request.is_json:
        update = request.get_json()
        
        if 'message' in update:
            chat_id = str(update['message']['chat']['id'])
            user_text = update['message'].get('text', '')
            
            # Обработка команды /clear
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
                # Запрос к Qwen через Puter.js
                answer = ask_qwen_puter(chat_histories[chat_id])
                
                # Добавляем ответ в историю
                chat_histories[chat_id].append({"role": "assistant", "content": answer})
                
                # Ограничиваем историю последними 10 сообщениями
                if len(chat_histories[chat_id]) > 10:
                    chat_histories[chat_id] = chat_histories[chat_id][-10:]
                
                send_message(chat_id, answer)
                
            except Exception as e:
                send_message(chat_id, f"❌ Ошибка: {str(e)}")
    
    return jsonify({"status": "ok"})

def ask_qwen_puter(messages):
    """Отправляет запрос к Qwen через Puter.js (бесплатно, без ключей)"""
    
    # Системный промпт
    system_prompt = {
        "role": "system",
        "content": """Ты — умный и дружелюбный ИИ-помощник для учёбы и работы.
Ты отлично знаешь русский язык. Отвечай полезно, понятно и по делу.
Помогай с учебой (объясняй темы, решай задачи) и с работой (письма, отчёты, идеи)."""
    }
    
    full_messages = [system_prompt] + messages
    
    # Формат запроса как в OpenAI API
    data = {
        "model": "qwen/qwen3.5-397b-a17b",  # Огромная модель Qwen 3.5 на 397B параметров[citation:1]
        "messages": full_messages,
        "temperature": 0.7,
        "max_tokens": 2000,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Отправляем запрос на публичный API Puter
    response = requests.post(
        PUTER_AI_URL,
        headers=headers,
        json=data,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        # Puter возвращает в стандартном OpenAI формате
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"Ошибка Puter API: {response.status_code} - {response.text}")

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
