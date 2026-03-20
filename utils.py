# utils.py
from datetime import datetime
from config import LOG_FILE
from storage import players_data, save_data


def error_logger(user: str, msg: str, error: Exception) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"\n{datetime.now().isoformat()} "
            f"Пользователь: {user} - Сообщение: {msg} - Ошибка: {error}\n"
        )


def get_player_data(message, user_id: str):
    """Получить/создать профиль игрока."""
    if user_id not in players_data:
        players_data[user_id] = {
            "name": message.from_user.username,
            "money": 100,
            "inventory": {"seeds": {}, "flowers": {}, "bonuses": {}},
            "garden": [],
            "last_notification": datetime.now().isoformat(),
            "total_income": 0,
            "max_garden": 5,
            "bouquets": [],
            "max_bouquets": 1,
            "previous_combos": [],
            "last_bonus_date": "",
            "recipes": [],
            "quest_progress": {
                "plant_count": 0,
                "harvest_count": 0,
                "water_count": 0,
                "earn_money": 0,
                "buy_seeds_count": 0,
            },
            "last_quest_date": "",
            "last_minigame_date": "",
        }
        return players_data[user_id], True

    return players_data[user_id], False
