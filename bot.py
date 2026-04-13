from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Bot is running"
    
    if request.is_json:
        update = request.get_json()
        
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            # Отправляем ответ
            send_message(chat_id, f"Ты написал: {text}")
    
    return jsonify({"status": "ok"})

def send_message(chat_id, text):
    try:
        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
    except Exception as e:
        print(e)

if __name__ == "__main__":
    app.run()
