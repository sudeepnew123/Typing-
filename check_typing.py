import time
import requests
from config import API_URL
from word_handler import get_random_word
from database import load_data, save_data

sessions = {}

def handle_typing_session(chat_id, user_id, difficulty):
    word = get_random_word(difficulty)
    sessions[user_id] = {
        "word": word,
        "start_time": time.time(),
        "difficulty": difficulty
    }
    send_message(chat_id, f"Type this word:\n\n`{word}`", parse_mode="Markdown")

def check_typing(chat_id, user_id, typed_text, username):
    session = sessions.get(user_id)
    if not session:
        return

    target_word = session["word"]
    time_taken = time.time() - session["start_time"]
    difficulty = session["difficulty"]

    if typed_text.strip() != target_word.strip():
        return  # Word didn't match

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
    user["username"] = username  # Update username

    data[str(user_id)] = user
    save_data(data)

    del sessions[user_id]

    message = (
        f"✅ Word matched!\n"
        f"Speed: {wpm:.2f} WPM\n"
        f"Accuracy: {accuracy:.1f}%\n"
        f"Points earned: {points}"
    )
    send_message(chat_id, message, reply_markup=get_next_button(difficulty))

def calculate_accuracy(original, typed):
    matches = sum(o == t for o, t in zip(original, typed))
    return (matches / len(original)) * 100 if original else 0

def calculate_wpm(text, seconds):
    words = len(text) / 5
    minutes = seconds / 60
    return words / minutes if minutes > 0 else 0

def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    payload = {'chat_id': chat_id, 'text': text}
    if parse_mode:
        payload['parse_mode'] = parse_mode
    if reply_markup:
        payload['reply_markup'] = reply_markup
    requests.post(f"{API_URL}/sendMessage", json=payload)

def get_next_button(difficulty):
    return {
        "inline_keyboard": [[
            {"text": "➡️ Next", "callback_data": difficulty}
        ]]
    }
