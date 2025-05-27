import requests
from config import API_URL
from database import load_data

def handle_leaderboard(chat_id):
    data = load_data()
    if not data:
        send_message(chat_id, "No data available yet.")
        return

    sorted_users = sorted(data.items(), key=lambda x: x[1].get('points', 0), reverse=True)
    top_users = sorted_users[:10]

    message = "🏆 *Typing Leaderboard*\n\n"
    for i, (user_id, stats) in enumerate(top_users, start=1):
        avg_wpm = stats["total_wpm"] / stats["games"] if stats["games"] else 0
        avg_accuracy = stats["total_accuracy"] / stats["games"] if stats["games"] else 0
        username = stats.get("username", "User")
        message += f"{i}. @{username} — {stats['points']} pts | {avg_wpm:.1f} WPM | {avg_accuracy:.1f}% Accuracy\n"

    send_message(chat_id, message, parse_mode="Markdown")

def send_message(chat_id, text, parse_mode=None):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    if parse_mode:
        payload['parse_mode'] = parse_mode
    requests.post(f"{API_URL}/sendMessage", json=payload)
