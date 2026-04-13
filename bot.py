from flask import Flask, request, jsonify
import requests
import os
import logging

# Настройка логов
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Bot is running"
    
    if request.is_json:
        update = request.get_json()
        
        # Логируем всё, что пришло от Telegram
        logging.info(f"Получен update: {update}")
        
        # Проверяем наличие сообщения
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            message = update['message']
            
            # Получаем текст или другой тип сообщения
            if 'text' in message:
                text = message['text']
                send_message(chat_id, f"Ты написал: {text}")
            else:
                # Если не текст, отвечаем так
                send_message(chat_id, f"Получил твоё сообщение, но это не текст!")
        else:
            logging.info("Нет поля message в update")
    
    return jsonify({"status": "ok"})

def send_message(chat_id, text):
    try:
        response = requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
        logging.info(f"Ответ от Telegram API: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Ошибка при отправке: {e}")

if __name__ == "__main__":
    app.run()
