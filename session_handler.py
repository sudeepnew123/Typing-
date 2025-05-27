import time
import requests
from config import API_URL
from word_handler import get_random_word
from database import load_data, save_data

sessions = {}
user_last_difficulty = {}  # Track last difficulty for each user

def handle_typing_session(chat_id, user_id, difficulty):
    word = get_random_word(difficulty)
    sessions[user_id] = {
        "word": word,
        "start_time": time.time(),
        "difficulty": difficulty
    }
    user_last_difficulty[user_id] = difficulty  # Save last difficulty
    send_word_with_next(chat_id, word)

def check_typing(chat_id, user_id, typed_text, username):
    session = sessions.get(user_id)
    if not session:
        return

    target_word = session["word"]
    time_taken = time.time() - session["start_time"]
    difficulty = session["difficulty"]

    accuracy = calculate_accuracy(target_word, typed_text)
    wpm = calculate_wpm(typed_text, time_taken)

    points = int(wpm * (accuracy / 100))
    data = load_data()

    user = data.get(str(user_id), {
        "username": username,
        "games": 0,
        "total_wpm": 0,
        "total_accuracy": 0,
        "points": 0
    })

    user["games"] += 1
    user["total_wpm"] += wpm
    user["total_accuracy"] += accuracy
    user["points"] += points
    user["username"] = username

    data[str(user_id)] = user
    save_data(data)

    del sessions[user_id]

    result_msg = f"✅ Word matched!\nSpeed: {wpm:.2f} WPM\nAccuracy: {accuracy:.1f}%\nPoints earned: {points}"
    send_message(chat_id, result_msg, reply_markup=get_next_button())

def calculate_accuracy(original, typed):
    matches = sum(o == t for o, t in zip(original, typed))
    return (matches / len(original)) * 100 if original else 0

def calculate_wpm(text, seconds):
    words = len(text) / 5
    minutes = seconds / 60
    return words / minutes if minutes > 0 else 0

def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    if parse_mode:
        payload['parse_mode'] = parse_mode
    if reply_markup:
        payload['reply_markup'] = reply_markup
    requests.post(f"{API_URL}/sendMessage", json=payload)

def send_word_with_next(chat_id, word):
    text = f"Type this word:\n\n`{word}`"
    reply_markup = get_next_button()
    send_message(chat_id, text, parse_mode="Markdown", reply_markup=reply_markup)

def get_next_button():
    return {
        "inline_keyboard": [[
            {"text": "➡️ Next", "callback_data": "next_word"}
        ]]
    }

def get_last_difficulty(user_id):
    return user_last_difficulty.get(user_id)
