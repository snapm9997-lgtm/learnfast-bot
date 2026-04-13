from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Настройки Telegram
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"

# Настройки OpenRouter
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Выбери модель ИИ (меняй здесь, какую хочешь):
# - "google/gemini-2.0-flash-exp:free" — Gemini (бесплатно, умный)
# - "meta-llama/llama-3.2-3b-instruct:free" — Llama (быстрый)
# - "microsoft/phi-3-mini-128k-instruct:free" — Phi-3 (маленький, быстрый)
# - "qwen/qwen-2.5-7b-instruct:free" — Qwen (хороший русский)
# - "deepseek/deepseek-chat:free" — DeepSeek (мощный)
MODEL = "openrouter/free"

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
            
            # Команды
            if user_text.startswith('/'):
                handle_command(chat_id, user_text)
                return jsonify({"status": "ok"})
            
            # Получаем историю для этого чата
            if chat_id not in chat_histories:
                chat_histories[chat_id] = []
            
            # Добавляем сообщение пользователя в историю
            chat_histories[chat_id].append({"role": "user", "content": user_text})
            
            try:
                # Запрос к OpenRouter
                response = ask_openrouter(chat_histories[chat_id])
                answer = response
                
                # Добавляем ответ в историю
                chat_histories[chat_id].append({"role": "assistant", "content": answer})
                
                # Ограничиваем историю последними 20 сообщениями (10 диалогов)
                if len(chat_histories[chat_id]) > 20:
                    chat_histories[chat_id] = chat_histories[chat_id][-20:]
                
                send_message(chat_id, answer)
                
            except Exception as e:
                send_message(chat_id, f"❌ Ошибка: {str(e)}")
    
    return jsonify({"status": "ok"})

def ask_openrouter(messages):
    """Отправляет запрос к OpenRouter и возвращает ответ"""
    
    # Системный промпт — объясняет боту его роль
    system_prompt = {
        "role": "system",
        "content": """Ты — умный и дружелюбный ИИ-помощник для учёбы и работы.
Твои особенности:
- Отвечаешь полезно, понятно и по делу
- Помогаешь с учебой (объясняешь темы, решаешь задачи, пересказываешь тексты)
- Помогаешь с работой (письма, отчёты, презентации, идеи)
- Используешь примеры и аналогии, чтобы было понятно
- Если не знаешь ответ — честно говоришь об этом
- Отвечаешь на том же языке, на котором спросили"""
    }
    
    # Формируем полный список сообщений
    full_messages = [system_prompt] + messages
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": full_messages,
        "temperature": 0.7,  # Творческость (0.1 — строгий, 1.0 — креативный)
        "max_tokens": 2000,   # Максимальная длина ответа
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"OpenRouter ошибка: {response.status_code} - {response.text}")

def handle_command(chat_id, command):
    """Обрабатывает команды"""
    if command == '/clear':
        if chat_id in chat_histories:
            del chat_histories[chat_id]
        send_message(chat_id, "🧹 История диалога очищена!")
    
    elif command == '/models':
        text = """📚 Доступные модели (меняй в коде):
1. gemini-2.0-flash — Gemini (умный, хороший русский)
2. llama-3.2 — Llama (быстрый)
3. phi-3-mini — Phi-3 (экономичный)
4. qwen-2.5 — Qwen (отличный русский)
5. deepseek-chat — DeepSeek (мощный)

Сейчас используется: """ + MODEL
        
        send_message(chat_id, text)
    
    elif command == '/help':
        text = """🤖 Команды бота:
/clear — очистить историю диалога
/models — показать доступные модели
/help — это сообщение

Просто пиши любые вопросы — я помогу с учёбой и работой!"""
        
        send_message(chat_id, text)
    else:
        send_message(chat_id, f"Неизвестная команда. Напиши /help для списка команд.")

def send_message(chat_id, text):
    """Отправляет сообщение в Telegram"""
    try:
        # Разбиваем длинные сообщения
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
