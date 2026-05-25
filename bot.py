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
# ... (предыдущий код)

@app.route('/miniapp')
def miniapp():
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <title>LearnFast | ИИ для бизнеса</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: var(--tg-theme-bg-color, #ffffff);
                color: var(--tg-theme-text-color, #000000);
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .header {
                padding: 16px;
                background: var(--tg-theme-secondary-bg-color, #f0f0f0);
                text-align: center;
                border-bottom: 1px solid var(--tg-theme-hint-color, #cccccc);
            }
            .header h1 {
                font-size: 20px;
                margin-bottom: 4px;
            }
            .header p {
                font-size: 12px;
                opacity: 0.7;
            }
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .message {
                max-width: 85%;
                padding: 10px 14px;
                border-radius: 18px;
                word-wrap: break-word;
                font-size: 15px;
                line-height: 1.4;
            }
            .message.user {
                align-self: flex-end;
                background: var(--tg-theme-button-color, #2481cc);
                color: var(--tg-theme-button-text-color, #fff);
                border-bottom-right-radius: 4px;
            }
            .message.assistant {
                align-self: flex-start;
                background: var(--tg-theme-secondary-bg-color, #e9ecef);
                color: var(--tg-theme-text-color, #000);
                border-bottom-left-radius: 4px;
            }
            .input-area {
                display: flex;
                padding: 12px;
                gap: 8px;
                background: var(--tg-theme-secondary-bg-color, #f5f5f5);
                border-top: 1px solid var(--tg-theme-hint-color, #ddd);
            }
            #userInput {
                flex: 1;
                padding: 10px 14px;
                border: none;
                border-radius: 24px;
                background: var(--tg-theme-bg-color, #fff);
                color: var(--tg-theme-text-color, #000);
                font-size: 15px;
                resize: none;
                font-family: inherit;
                outline: none;
            }
            .send-btn {
                width: 44px;
                height: 44px;
                border: none;
                border-radius: 50%;
                background: var(--tg-theme-button-color, #2481cc);
                color: var(--tg-theme-button-text-color, #fff);
                font-size: 20px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .features {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                padding: 12px;
                background: var(--tg-theme-secondary-bg-color, #f5f5f5);
                border-top: 1px solid var(--tg-theme-hint-color, #ddd);
            }
            .feature-btn {
                flex: 1;
                min-width: 90px;
                padding: 8px 12px;
                border: none;
                border-radius: 20px;
                background: var(--tg-theme-bg-color, #fff);
                color: var(--tg-theme-text-color, #000);
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 LearnFast Business</h1>
            <p>ИИ-агент для маркетинга, продаж и контента</p>
        </div>
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message assistant">
                    Привет! Я твой ИИ-агент для бизнеса. Чем могу помочь?
                    
                    ✅ Написать письмо клиенту
                    ✅ Придумать пост для Telegram
                    ✅ Проанализировать отзывы
                    ✅ Составить оффер
                    
                    Просто опиши задачу!
                </div>
            </div>
            <div class="input-area">
                <textarea id="userInput" placeholder="Напиши сообщение..." rows="1"></textarea>
                <button class="send-btn" id="sendBtn">📤</button>
            </div>
        </div>
        <div class="features">
            <button class="feature-btn" data-prompt="Напиши продающий пост для Telegram о [товаре/услуге]">📱 Пост в TG</button>
            <button class="feature-btn" data-prompt="Напиши холодное письмо клиенту, который хочет [услуга]">✉️ Письмо</button>
            <button class="feature-btn" data-prompt="Составь оффер для [ниша]">🎯 Оффер</button>
            <button class="feature-btn" data-prompt="Сделай SWOT-анализ для [бизнес-идея]">📊 SWOT</button>
        </div>
        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();
            tg.enableClosingConfirmation();
            
            const messagesContainer = document.getElementById('messages');
            const userInput = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            
            let isLoading = false;
            
            function addMessage(text, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                messageDiv.textContent = text;
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                return messageDiv;
            }
            
            async function sendToBot(message) {
                if (isLoading) return;
                
                addMessage(message, 'user');
                userInput.value = '';
                
                isLoading = true;
                const loadingMsg = addMessage('✍️ Печатает...', 'assistant');
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    loadingMsg.remove();
                    addMessage(data.reply, 'assistant');
                    
                } catch (error) {
                    loadingMsg.remove();
                    addMessage('❌ Ошибка. Попробуй позже.', 'assistant');
                }
                
                isLoading = false;
            }
            
            sendBtn.addEventListener('click', () => {
                const text = userInput.value.trim();
                if (text) sendToBot(text);
            });
            
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const text = userInput.value.trim();
                    if (text) sendToBot(text);
                }
            });
            
            document.querySelectorAll('.feature-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    let prompt = btn.dataset.prompt;
                    userInput.value = prompt;
                    userInput.focus();
                });
            });
            
            tg.ready();
        </script>
    </body>
    </html>
    '''
