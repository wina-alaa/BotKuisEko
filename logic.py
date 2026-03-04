import json
import random
import os
from config import DATA_FILE, QUIZ_FILE

# LOAD & SAVE USER DATA

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# LOAD QUIZ DATA

def load_quiz():
    with open(QUIZ_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

quiz_levels = load_quiz()

# AMBIL / BUAT USER

def get_user(user_id):
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "money": 0
        }
        save_data(data)

    return data[user_id]

# AMBIL 1 SOAL RANDOM SESUAI LEVEL

def get_random_question(level):
    level = str(level)

    if level not in quiz_levels:
        return None

    question = random.choice(quiz_levels[level]["quiz_list"])
    return question

# CEK JAWABAN

def check_answer(user_id, level, question, user_answer):
    data = load_data()
    user = get_user(user_id)

    correct_answer = question["answer"].upper()

    if user_answer.upper() == correct_answer:
        reward = quiz_levels[str(level)]["reward"]
        user["money"] += reward

        data[str(user_id)] = user
        save_data(data)

        return True, reward
    else:
        return False, 0

# CEK UANG USER

def get_balance(user_id):
    user = get_user(user_id)
    return user["money"]