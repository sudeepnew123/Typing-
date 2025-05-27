from flask import Flask, request
import os
import requests
from config import API_URL
from word_handler import get_random_word
from session_handler import handle_typing_session, check_typing
from leaderboard_handler import handle_leaderboard
from admin import handle_admin_command

app = Flask(__name__)

@app.route('/')
def home():
    return "Typing Speed Bot is running!"

@app.route(f'/{os.getenv("BOT_TOKEN")}', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return "no data"

    # Handle message or callback_query
    if "message" in data:
        message = data['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from'].get('username') or message['from'].get('first_name', 'User')
        text = message.get('text', '')

        # Command handling
        if text == '/start':
            send_message(chat_id, "Welcome to Typing Speed Bot! Choose difficulty:", reply_markup=get_category_buttons())
        elif text == '/leaderboard':
            handle_leaderboard(chat_id)
        elif text.startswith('/broadcast') or text.startswith('/resetdata'):
            handle_admin_command(user_id, chat_id, text)
        elif text.lower() in ['easy', 'medium', 'hard']:
            handle_typing_session(chat_id, user_id, text.lower())
        else:
            check_typing(chat_id, user_id, text, user_name)

    elif "callback_query" in data:
        query = data['callback_query']
        chat_id = query['message']['chat']['id']
        user_id = query['from']['id']
        difficulty = query['data']
        handle_typing_session(chat_id, user_id, difficulty.lower())

    return "ok"

def send_message(chat_id, text, reply_markup=None):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    requests.post(f"{API_URL}/sendMessage", json=payload)

def get_category_buttons():
    return {
        "inline_keyboard": [
            [{"text": "🟢 Easy", "callback_data": "easy"}],
            [{"text": "🟡 Medium", "callback_data": "medium"}],
            [{"text": "🔴 Hard", "callback_data": "hard"}]
        ]
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
