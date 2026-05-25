from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# ФИКСИРОВАННАЯ УМНАЯ МОДЕЛЬ (самая мощная из бесплатных)
MODEL = "google/gemini-2.0-flash-exp:free"

URL = f"https://api.telegram.org/bot{TOKEN}"
MINI_APP_URL = "https://learnfast-bot.vercel.app/miniapp"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "✅ Бот и Mini App работают"
    return jsonify({"status": "ok"})

@app.route('/miniapp')
def miniapp():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <title>LearnFast Business | Portal</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', system-ui, -apple-system;
                background: radial-gradient(circle at 20% 30%, #0a0f1e, #03050b);
                color: #ffffff;
                min-height: 100vh;
                padding: 12px;
            }
            .glow {
                position: fixed;
                top: -20%;
                left: -20%;
                width: 140%;
                height: 140%;
                background: radial-gradient(circle, rgba(0,242,255,0.15), transparent 70%);
                pointer-events: none;
                animation: pulse 6s ease infinite;
                z-index: 0;
            }
            @keyframes pulse {
                0% { opacity: 0.3; transform: scale(1);}
                50% { opacity: 0.6; transform: scale(1.03);}
                100% { opacity: 0.3; transform: scale(1);}
            }
            .container {
                position: relative;
                z-index: 2;
                max-width: 600px;
                margin: 0 auto;
            }
            .hero {
                background: rgba(10,20,30,0.6);
                backdrop-filter: blur(12px);
                border-radius: 32px;
                padding: 20px;
                text-align: center;
                margin-bottom: 16px;
                border: 1px solid cyan;
            }
            .hero h1 {
                font-size: 28px;
                background: linear-gradient(135deg, #fff, cyan, magenta);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            .hero p {
                font-size: 12px;
                opacity: 0.8;
                margin-top: 8px;
            }
            .capabilities {
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(8px);
                border-radius: 24px;
                padding: 16px;
                margin-bottom: 16px;
                border: 1px solid rgba(0,242,255,0.3);
            }
            .capabilities h3 {
                font-size: 16px;
                margin-bottom: 12px;
                color: cyan;
            }
            .capabilities ul {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                list-style: none;
            }
            .capabilities li {
                background: rgba(0,242,255,0.1);
                border: 1px solid cyan;
                border-radius: 40px;
                padding: 6px 14px;
                font-size: 12px;
            }
            .chat-container {
                background: rgba(12,18,28,0.65);
                backdrop-filter: blur(16px);
                border-radius: 32px;
                border: 1px solid cyan;
                overflow: hidden;
                margin-bottom: 12px;
            }
            .messages {
                height: 45vh;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .message {
                max-width: 85%;
                padding: 12px 16px;
                border-radius: 24px;
                font-size: 14px;
                line-height: 1.4;
            }
            .message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, #00c6ff, #0072ff);
                color: white;
            }
            .message.assistant {
                align-self: flex-start;
                background: #2a3a4a;
                border-left: 3px solid cyan;
            }
            .input-area {
                display: flex;
                gap: 8px;
                padding: 12px;
                border-top: 1px solid cyan;
            }
            #userInput {
                flex: 1;
                background: #1e2a3a;
                border: 1px solid cyan;
                border-radius: 48px;
                padding: 12px;
                color: white;
                outline: none;
                font-size: 14px;
            }
            .send-btn {
                background: cyan;
                border: none;
                border-radius: 48px;
                padding: 0 20px;
                font-weight: bold;
                cursor: pointer;
                color: black;
            }
            .status {
                text-align: center;
                font-size: 11px;
                padding: 8px;
                opacity: 0.7;
            }
        </style>
    </head>
    <body>
        <div class="glow"></div>
        <div class="container">
            <div class="hero">
                <h1>⚡ LEARNFAST ⚡</h1>
                <p>ИИ-портал для бизнеса</p>
            </div>

            <div class="capabilities">
                <h3>✨ Что умеет этот ИИ:</h3>
                <ul>
                    <li>📝 Писать посты для Telegram</li>
                    <li>✉️ Составлять письма и коммерческие предложения</li>
                    <li>📊 Анализировать рынок и конкурентов (SWOT)</li>
                    <li>💡 Генерировать идеи для бизнеса</li>
                    <li>📈 Создавать контент-планы и стратегии</li>
                    <li>🛠️ Помогать с запуском продуктов</li>
                    <li>📄 Пересказывать и структурировать текст</li>
                    <li>🌍 Переводить на любые языки</li>
                    <li>🧠 Работает с Gemini 2.0 — умная нейросеть</li>
                </ul>
            </div>

            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message assistant">🚀 Портал открыт! Напиши свою задачу, и я помогу.</div>
                </div>
                <div class="input-area">
                    <input type="text" id="userInput" placeholder="Напиши сообщение...">
                    <button class="send-btn" id="sendBtn">📤</button>
                </div>
            </div>
            <div class="status">
                ⚡ Модель: Google Gemini 2.0 Flash
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();
            tg.ready();

            const messagesDiv = document.getElementById('messages');
            const userInput = document.getElementById('userInput');
            const sendBtn = document.getElementById('sendBtn');
            let isLoading = false;

            function addMessage(text, sender) {
                const div = document.createElement('div');
                div.className = `message ${sender}`;
                div.innerText = text;
                messagesDiv.appendChild(div);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return div;
            }

            async function sendMessageToBot(text) {
                if (isLoading) return;
                addMessage(text, 'user');
                userInput.value = '';
                isLoading = true;
                const loadingMsg = addMessage('🌀 Думаю...', 'assistant');

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
                const val = userInput.value.trim();
                if (val) sendMessageToBot(val);
            };

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const val = userInput.value.trim();
                    if (val) sendMessageToBot(val);
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    user_message = data.get('message', '')

    system_prompt = {
        "role": "system",
        "content": """Ты — экспертный ИИ-помощник для бизнеса, маркетинга и предпринимателей.
Твои качества:
- Отвечаешь максимально полезно, конкретно и без воды
- Даёшь готовые решения, а не общие слова
- Умеешь писать продающие тексты, анализировать, предлагать идеи
- Знаешь русский язык на уровне носителя
- Если нужно что-то уточнить — задаёшь наводящие вопросы
- Отвечаешь дружелюбно, но профессионально"""
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
                "max_tokens": 2500
            },
            timeout=90
        )

        if resp.status_code == 200:
            reply = resp.json()['choices'][0]['message']['content']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"Ошибка API: {resp.status_code}"}), 500
    except Exception as e:
        return jsonify({"reply": f"Ошибка: {str(e)[:150]}"}), 500

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
