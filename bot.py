from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Стабильная бесплатная модель
MODEL = "meta-llama/llama-4-maverick:free"

URL = f"https://api.telegram.org/bot{TOKEN}"
MINI_APP_URL = "https://learnfast-bot.vercel.app/miniapp"

# --------------------- TELEGRAM WEBHOOT ---------------------
@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "✅ Бот и Mini App работают"

    if request.is_json:
        update = request.get_json()
        if 'message' in update:
            chat_id = str(update['message']['chat']['id'])
            text = update['message'].get('text', '')

            if text == '/start':
                keyboard = {
                    "inline_keyboard": [[{
                        "text": "🚀 Открыть Mini App",
                        "web_app": {"url": MINI_APP_URL}
                    }]]
                }
                send_message(
                    chat_id,
                    "🤖 Привет! Я — ИИ-помощник для бизнеса.\n👇 Нажми на кнопку, чтобы открыть приложение:",
                    keyboard
                )
                return jsonify({"status": "ok"})

            send_message(chat_id, "Используй кнопку, чтобы открыть приложение 👆")
    return jsonify({"status": "ok"})

# --------------------- MINI APP СТРАНИЦА ---------------------
@app.route('/miniapp')
def miniapp():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <title>LearnFast Business</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
                border-bottom: 1px solid var(--tg-theme-hint-color, #ccc);
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
                font-size: 15px;
                line-height: 1.4;
            }
            .message.user {
                align-self: flex-end;
                background: var(--tg-theme-button-color, #2481cc);
                color: white;
                border-bottom-right-radius: 4px;
            }
            .message.assistant {
                align-self: flex-start;
                background: var(--tg-theme-secondary-bg-color, #e9ecef);
                color: black;
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
                color: white;
                font-size: 20px;
                cursor: pointer;
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
                font-size: 12px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 LearnFast Business</h1>
            <p>ИИ для маркетинга, продаж и контента</p>
        </div>
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message assistant">
                    Привет! Я твой ИИ-агент для бизнеса.<br><br>
                    ✅ Написать письмо клиенту<br>
                    ✅ Пост для Telegram<br>
                    ✅ Анализ отзывов<br>
                    ✅ Оффер и SWOT<br><br>
                    Просто напиши задачу!
                </div>
            </div>
            <div class="input-area">
                <textarea id="userInput" placeholder="Напиши сообщение..." rows="1"></textarea>
                <button class="send-btn" id="sendBtn">📤</button>
            </div>
        </div>
        <div class="features">
            <button class="feature-btn" data-prompt="Напиши продающий пост для Telegram о моём продукте">📱 Пост в TG</button>
            <button class="feature-btn" data-prompt="Напиши холодное письмо для клиента">✉️ Письмо</button>
            <button class="feature-btn" data-prompt="Сделай SWOT-анализ для моего бизнеса">📊 SWOT</button>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();
            tg.enableClosingConfirmation();

            const messagesDiv = document.getElementById('messages');
            const userInput = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');

            let isLoading = false;

            function addMessage(text, sender) {
                const msg = document.createElement('div');
                msg.className = `message ${sender}`;
                msg.textContent = text;
                messagesDiv.appendChild(msg);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return msg;
            }

            async function sendMessageToBot(text) {
                if (isLoading) return;
                addMessage(text, 'user');
                userInput.value = '';
                isLoading = true;

                const loadingMsg = addMessage('✍️ Печатает...', 'assistant');

                try {
                    const res = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text })
                    });
                    const data = await res.json();
                    loadingMsg.remove();
                    addMessage(data.reply || '❌ Ошибка', 'assistant');
                } catch (err) {
                    loadingMsg.remove();
                    addMessage('❌ Ошибка сервера', 'assistant');
                }
                isLoading = false;
            }

            sendBtn.onclick = () => {
                const text = userInput.value.trim();
                if (text) sendMessageToBot(text);
            };

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const text = userInput.value.trim();
                    if (text) sendMessageToBot(text);
                }
            });

            document.querySelectorAll('.feature-btn').forEach(btn => {
                btn.onclick = () => {
                    userInput.value = btn.dataset.prompt;
                    userInput.focus();
                };
            });

            tg.ready();
        </script>
    </body>
    </html>
    '''

# --------------------- ЧАТ ДЛЯ MINI APP ---------------------
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    user_message = data.get('message', '')

    system_prompt = {
        "role": "system",
        "content": "Ты — ИИ-помощник для бизнеса. Помогаешь с маркетингом, продажами, письмами, контентом. Отвечай чётко и по делу."
    }

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [system_prompt, {"role": "user", "content": user_message}],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=60
        )

        if resp.status_code == 200:
            reply = resp.json()['choices'][0]['message']['content']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"Ошибка API: {resp.status_code}"}), 500
    except Exception as e:
        return jsonify({"reply": f"Ошибка: {str(e)}"}), 500

# --------------------- ОТПРАВКА СООБЩЕНИЙ ---------------------
def send_message(chat_id, text, reply_markup=None):
    try:
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        requests.post(f"{URL}/sendMessage", json=payload)
    except Exception as e:
        print("Ошибка отправки:", e)

if __name__ == "__main__":
    app.run()
