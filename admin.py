import requests
from config import API_URL, ADMIN_ID
from database import save_data, load_data

def handle_admin_command(user_id, chat_id, text):
    if user_id != ADMIN_ID:
        send_message(chat_id, "You are not authorized to use this command.")
        return

    if text.startswith("/broadcast"):
        msg = text.replace("/broadcast", "").strip()
        if not msg:
            send_message(chat_id, "Please provide a message to broadcast.")
            return

        data = load_data()
        sent = 0
        for uid in data.keys():
            try:
                send_message(uid, f"📢 Broadcast:\n\n{msg}")
                sent += 1
            except:
                continue
        send_message(chat_id, f"Broadcast sent to {sent} users.")

    elif text.startswith("/resetdata"):
        save_data({})
        send_message(chat_id, "All user data has been reset.")

def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(f"{API_URL}/sendMessage", json=payload)
