# minigames.py

from datetime import datetime
import random

from storage import players_data, save_data
from game_data import flower_combinations
from bot_instance import bot


# Вопросы для мини-игры викторины
quiz_questions = [
    {
        "question": "Какой цветок считается символом любви?",
        "options": ["Роза", "Тюльпан", "Лилии", "Пион"],
        "correct": 0,
    },
    {
        "question": "Какой цветок цветет весной одним из первых?",
        "options": ["Роза", "Нарцисс", "Герань", "Петуния"],
        "correct": 1,
    },
    {
        "question": "Какой цветок известен своим ароматом и используется в парфюмерии?",
        "options": ["Астра", "Лаванда", "Календула", "Барвинок"],
        "correct": 1,
    },
    {
        "question": "Какой цветок называют 'королевой цветов'?",
        "options": ["Пион", "Роза", "Орхидея", "Лилия"],
        "correct": 1,
    },
    {
        "question": "Какой цветок является символом Японии?",
        "options": ["Роза", "Тюльпан", "Сакура", "Лаванда"],
        "correct": 2,
    },
    {
        "question": "Какой цветок растет в воде?",
        "options": ["Лотос", "Роза", "Тюльпан", "Нарцисс"],
        "correct": 0,
    },
    {
        "question": "Какой цветок имеет название, связанное с солнцем?",
        "options": ["Подсолнух", "Роза", "Лилии", "Пион"],
        "correct": 0,
    },
    {
        "question": "Какой цветок цветет ночью?",
        "options": ["Роза", "Ночная фиалка", "Тюльпан", "Нарцисс"],
        "correct": 1,
    },
]


def start_minigame_quiz(user_id: str):
    if user_id not in players_data:
        return None

    player = players_data[user_id]
    today = datetime.now().date().isoformat()
    dates = player.setdefault("last_minigame_dates", {})
    if dates.get("quiz") == today:
        return None

    question = random.choice(quiz_questions)

    player["minigame"] = {
        "type": "quiz",
        "question": question,
        "started_at": datetime.now().isoformat(),
    }
    dates["quiz"] = today
    player["last_minigame_date"] = today
    save_data()

    return question


def start_minigame_guess(user_id: str):
    if user_id not in players_data:
        return None

    player = players_data[user_id]
    today = datetime.now().date().isoformat()
    dates = player.setdefault("last_minigame_dates", {})
    if dates.get("guess") == today:
        return None

    secret_number = random.randint(1, 100)

    player["minigame"] = {
        "type": "guess",
        "secret_number": secret_number,
        "attempts": 0,
        "max_attempts": 7,
        "started_at": datetime.now().isoformat(),
    }
    dates["guess"] = today
    player["last_minigame_date"] = today
    save_data()

    return player["minigame"]


def complete_minigame(user_id: str, correct: bool) -> bool:
    """Завершает мини-игру и выдает награду"""
    if user_id not in players_data:
        return False

    player = players_data[user_id]

    if "minigame" not in player:
        return False

    minigame = player["minigame"]

    if correct:
        # Выдаем рецепт за победу (для обеих игр)
        combo_name = random.choice(list(flower_combinations.keys()))
        combo_data = flower_combinations[combo_name]

        if "recipes" not in player:
            player["recipes"] = []

        # Проверяем, нет ли уже этого рецепта
        recipe_exists = any(r.get("name") == combo_name for r in player["recipes"])

        if not recipe_exists:
            recipe = {
                "name": combo_name,
                "flowers": combo_data["flowers"],
                "effect": combo_data["effect"],
                "description": combo_data["description"],
                "obtained_date": datetime.now().isoformat(),
            }
            player["recipes"].append(recipe)

            flowers_text = ", ".join(combo_data["flowers"])

            if minigame["type"] == "quiz":
                message = "🎉 <b>Правильный ответ!</b>\n\n"
            else:  # guess
                attempts = minigame.get("attempts", 0)
                message = "🎉 <b>Поздравляю с победой!</b>\n\n"
                message += f"🎯 Попыток использовано: {attempts}\n\n"

            message += "🎁 <b>Награда:</b> Рецепт комбинации!\n\n"
            message += f"📜 <b>{combo_name}</b>\n"
            message += f"🌸 Цветы: {flowers_text}\n"
            message += f"✨ Эффект: {combo_data['effect']}\n"
            message += f"📝 {combo_data['description']}"

            try:
                bot.send_message(int(user_id), message, parse_mode="HTML")
            except Exception:
                pass
        else:
            # Если рецепт уже есть, даем монеты
            bonus_money = 30
            player["money"] += bonus_money

            if minigame["type"] == "quiz":
                win_message = "Правильный ответ!"
            else:
                win_message = "Поздравляю с победой!"

            try:
                bot.send_message(
                    int(user_id),
                    f"🎉 <b>{win_message}</b>\n\n"
                    f"💰 Вы уже знаете этот рецепт, поэтому получаете {bonus_money} 🪙!",
                    parse_mode="HTML",
                )
            except Exception:
                pass

    # Удаляем состояние мини-игры
    if "minigame" in player:
        del player["minigame"]

    save_data()
    return True
