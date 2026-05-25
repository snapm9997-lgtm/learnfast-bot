from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = "openrouter/free"

URL = f"https://api.telegram.org/bot{TOKEN}"
MINI_APP_URL = "https://learnfast-bot.vercel.app/miniapp"

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
                        "text": "🚀 OPEN",
                        "web_app": {"url": MINI_APP_URL}
                    }]]
                }
                send_message(
                    chat_id,
                    "🌟 **LearnFast Business** — твой ИИ-помощник будущего.\n👇 Нажми OPEN, чтобы войти:",
                    keyboard
                )
                return jsonify({"status": "ok"})

            send_message(chat_id, "Используй кнопку OPEN 👆")
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
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', 'Poppins', system-ui, -apple-system, 'Orbitron', monospace;
                background: radial-gradient(circle at 20% 30%, #0a0f1e, #03050b);
                color: #ffffff;
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }

            /* Кибер-сетка на фоне */
            body::before {
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(#00f2ff22 1px, transparent 1px),
                    linear-gradient(90deg, #00f2ff22 1px, transparent 1px);
                background-size: 40px 40px;
                pointer-events: none;
                z-index: 0;
            }

            /* Голографический ореол */
            .glow {
                position: fixed;
                top: -20%;
                left: -20%;
                width: 140%;
                height: 140%;
                background: radial-gradient(circle, rgba(0,242,255,0.15), transparent 70%);
                pointer-events: none;
                z-index: 0;
                animation: pulse 8s ease infinite;
            }

            @keyframes pulse {
                0% { opacity: 0.3; transform: scale(1);}
                50% { opacity: 0.7; transform: scale(1.05);}
                100% { opacity: 0.3; transform: scale(1);}
            }

            .container {
                position: relative;
                z-index: 2;
                max-width: 600px;
                margin: 0 auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }

            /* header будущего */
            .hero {
                background: rgba(10, 20, 30, 0.6);
                backdrop-filter: blur(12px);
                border-radius: 32px;
                padding: 20px 16px;
                margin-bottom: 20px;
                border: 1px solid rgba(0, 242, 255, 0.4);
                box-shadow: 0 8px 32px rgba(0, 242, 255, 0.2);
                text-align: center;
            }

            .hero h1 {
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(135deg, #FFFFFF, #00f2ff, #b500ff);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                letter-spacing: 1px;
            }

            .hero p {
                font-size: 12px;
                opacity: 0.8;
                margin-top: 8px;
                font-family: monospace;
            }

            /* окно чата — стекло */
            .chat-container {
                flex: 1;
                background: rgba(12, 18, 28, 0.65);
                backdrop-filter: blur(16px);
                border-radius: 32px;
                border: 1px solid rgba(0, 242, 255, 0.3);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                margin-bottom: 12px;
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
                padding: 12px 16px;
                border-radius: 24px;
                font-size: 15px;
                line-height: 1.4;
                animation: fadeIn 0.2s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(6px);}
                to { opacity: 1; transform: translateY(0);}
            }

            .message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, #00c6ff, #0072ff);
                color: white;
                border-bottom-right-radius: 6px;
                box-shadow: 0 2px 8px rgba(0,114,255,0.3);
            }

            .message.assistant {
                align-self: flex-start;
                background: rgba(30, 40, 55, 0.8);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(0,242,255,0.3);
                color: #f0f0ff;
                border-bottom-left-radius: 6px;
            }

            /* панель ввода */
            .input-area {
                display: flex;
                gap: 12px;
                padding: 12px;
                background: rgba(0,0,0,0.5);
                border-top: 1px solid rgba(0,242,255,0.3);
            }

            #userInput {
                flex: 1;
                background: rgba(20, 30, 45, 0.9);
                border: 1px solid #00f2ff88;
                border-radius: 48px;
                padding: 12px 18px;
                color: white;
                font-size: 15px;
                font-family: inherit;
                outline: none;
                backdrop-filter: blur(8px);
                transition: 0.2s;
            }

            #userInput:focus {
                border-color: #ff00c8;
                box-shadow: 0 0 12px #ff00c8;
            }

            .send-btn {
                width: 52px;
                height: 52px;
                border-radius: 52px;
                background: linear-gradient(145deg, #00f2ff, #0066ff);
                border: none;
                font-size: 24px;
                cursor: pointer;
                transition: 0.2s;
                box-shadow: 0 0 8px cyan;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .send-btn:active {
                transform: scale(0.94);
            }

            /* КНОПКИ В СТИЛЕ MEME MINING */
            .features {
                display: flex;
                gap: 12px;
                justify-content: space-between;
                margin-top: 4px;
                margin-bottom: 12px;
            }

            .feature-btn {
                flex: 1;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid cyan;
                border-radius: 60px;
                padding: 12px 6px;
                font-weight: bold;
                font-size: 13px;
                color: #ffffff;
                text-shadow: 0 0 4px cyan;
                transition: 0.2s;
                cursor: pointer;
                text-align: center;
                letter-spacing: 1px;
            }

            .feature-btn:active {
                transform: scale(0.96);
                background: cyan;
                color: black;
                border-color: white;
            }

            /* скролл */
            ::-webkit-scrollbar {
                width: 4px;
            }
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            ::-webkit-scrollbar-thumb {
                background: cyan;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="glow"></div>
        <div class="container">
            <div class="hero">
                <h1>⚡ LEARNFAST ⚡</h1>
                <p>✦ BUSINESS AI · FUTURE PORTAL ✦</p>
            </div>

            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message assistant">
                        🚀 **Портал открыт.**<br><br>
                        Я — твой ИИ-агент для бизнеса.<br>
                        ✔ Маркетинг & Продажи<br>
                        ✔ Контент & Письма<br>
                        ✔ Аналитика & Офферы<br><br>
                        <span style="color:#00f2ff;">Напиши задачу — я решу её за секунды.</span>
                    </div>
                </div>
                <div class="input-area">
                    <textarea id="userInput" placeholder="✏️ Напиши сообщение..." rows="1"></textarea>
                    <button class="send-btn" id="sendBtn">📤</button>
                </div>
            </div>

            <div class="features">
                <div class="feature-btn" data-prompt="Напиши продающий пост для Telegram о моём продукте">📱 TG ПОСТ</div>
                <div class="feature-btn" data-prompt="Напиши холодное письмо, которое продаёт">✉️ ПИСЬМО</div>
                <div class="feature-btn" data-prompt="Сделай SWOT-анализ для бизнеса">📊 SWOT</div>
            </div>
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
                const div = document.createElement('div');
                div.className = `message ${sender}`;
                div.innerHTML = text.replace(/\\n/g, '<br>');
                messagesDiv.appendChild(div);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return div;
            }

            async function sendMessageToBot(rawText) {
                if (isLoading) return;
                addMessage(rawText, 'user');
                userInput.value = '';
                isLoading = true;
                const loadingMsg = addMessage('🌀 Генерация...', 'assistant');

                try {
                    const res = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: rawText })
                    });
                    const data = await res.json();
                    loadingMsg.remove();
                    addMessage(data.reply || '⚠️ Ошибка генерации', 'assistant');
                } catch (err) {
                    loadingMsg.remove();
                    addMessage('❌ Портал временно недоступен', 'assistant');
                }
                isLoading = false;
            }

            sendBtn.onclick = () => {
                const val = userInput.value.trim();
                if (val) sendMessageToBot(val);
            };

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const val = userInput.value.trim();
                    if (val) sendMessageToBot(val);
                }
            });

            document.querySelectorAll('.feature-btn').forEach(btn => {
                btn.onclick = () => {
                    userInput.value = btn.getAttribute('data-prompt');
                    userInput.focus();
                };
            });

            tg.ready();
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
        "content": "Ты — ИИ-помощник для бизнеса. Говори дерзко, чётко, продающе. Пиши по делу, без воды."
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
                "temperature": 0.75,
                "max_tokens": 1800
            },
            timeout=70
        )

        if resp.status_code == 200:
            reply = resp.json()['choices'][0]['message']['content']
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"⚡ API ошибка {resp.status_code}"}), 500
    except Exception as e:
        return jsonify({"reply": f"🔥 Ошибка: {str(e)[:100]}"}), 500

def send_message(chat_id, text, reply_markup=None):
    try:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        requests.post(f"{URL}/sendMessage", json=payload)
    except Exception as e:
        print("Ошибка отправки:", e)

if __name__ == "__main__":
    app.run()
