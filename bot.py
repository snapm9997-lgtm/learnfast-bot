import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Твой токен (замени на свой!)
BOT_TOKEN = "8667737788:AAGszVcI8BcrXdPcrBSTF_JGDDYZxsOMt3M"

# Команда для проверки, что бот жив
@app.route('/', methods=['GET'])
def index():
    return "Bot is running!"

# Вебхук — сюда Telegram будет присылать сообщения
@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        # Обработка команды /start
        if text == '/start':
            reply = "👋 Привет! Я учебный помощник.\n\nПришли мне вопрос по учёбе, и я постараюсь помочь!"
        else:
            # Здесь позже подключим OpenAI
            reply = f"Ты написал: {text}\n\n(функция с ИИ настраивается)"
        
        # Отправляем ответ
        send_message(chat_id, reply)
    
    return jsonify({"status": "ok"})

def send_message(chat_id, text):
    """Отправляет сообщение через Telegram Bot API"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run()
