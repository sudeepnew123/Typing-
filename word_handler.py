import random

def get_random_word(difficulty):
    file_path = f"words/{difficulty}.txt"
    try:
        with open(file_path, "r") as f:
            words = f.read().splitlines()
        return random.choice(words)
    except FileNotFoundError:
        return "default"
