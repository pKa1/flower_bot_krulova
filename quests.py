# quests.py
from datetime import datetime
import random
from storage import players_data, save_data
from game_data import flower_combinations
from bot_instance import bot

daily_quests = [
    {
        "type": "plant_count",
        "name": "Посади растения",
        "description": "Посади 5 любых растений.",
        "target": 5,
        "reward_type": "recipe",
    },
    # ... остальные задания как в исходном коде
]


def get_daily_quest(user_id: str):
    if user_id not in players_data:
        return None

    player = players_data[user_id]
    today = datetime.now().date().isoformat()
    last_quest_date = player.get("last_quest_date", "")

    if last_quest_date == today and "current_quest" in player:
        quest = player["current_quest"].copy()
        quest_type = quest["type"]
        quest["progress"] = player.get("quest_progress", {}).get(quest_type, 0)
        return quest

    quest = random.choice(daily_quests).copy()
    quest["progress"] = 0
    quest["completed"] = False

    player["current_quest"] = quest
    player["last_quest_date"] = today
    player["quest_progress"] = {
        "plant_count": 0,
        "harvest_count": 0,
        "water_count": 0,
        "earn_money": 0,
        "buy_seeds_count": 0,
    }
    save_data()
    return quest


def update_quest_progress(user_id: str, quest_type: str, amount: int = 1):
    if user_id not in players_data:
        return

    player = players_data[user_id]
    today = datetime.now().date().isoformat()

    if player.get("last_quest_date") != today:
        return
    if "current_quest" not in player:
        return

    quest = player["current_quest"]

    if quest["type"] != quest_type:
        return

    progress = player.setdefault("quest_progress", {}).setdefault(quest_type, 0)
    progress += amount
    player["quest_progress"][quest_type] = progress
    quest["progress"] = progress

    if progress >= quest["target"] and not quest.get("completed", False):
        quest["completed"] = True
        give_quest_reward(user_id, quest)

    save_data()


def give_quest_reward(user_id: str, quest: dict):
    if user_id not in players_data:
        return

    player = players_data[user_id]

    if quest["reward_type"] != "recipe":
        return

    combo_name = random.choice(list(flower_combinations.keys()))
    combo_data = flower_combinations[combo_name]

    recipes = player.setdefault("recipes", [])
    recipe_exists = any(r.get("name") == combo_name for r in recipes)

    if not recipe_exists:
        recipe = {
            "name": combo_name,
            "flowers": combo_data["flowers"],
            "effect": combo_data["effect"],
            "description": combo_data["description"],
            "obtained_date": datetime.now().isoformat(),
        }
        recipes.append(recipe)

        flowers_text = ", ".join(combo_data["flowers"])
        message = (
            "🎉 <b>Задание выполнено!</b>\n\n"
            "🎁 <b>Награда:</b> Рецепт комбинации!\n\n"
            f"📜 <b>{combo_name}</b>\n"
            f"🌸 Цветы: {flowers_text}\n"
            f"✨ Эффект: {combo_data['effect']}\n"
            f"📝 {combo_data['description']}\n\n"
            "💡 Используйте /recipes для просмотра всех рецептов!"
        )
        try:
            bot.send_message(int(user_id), message, parse_mode="HTML")
        except Exception:
            pass

        save_data()
    else:
        bonus_money = 50
        player["money"] += bonus_money
        try:
            bot.send_message(
                int(user_id),
                "🎉 <b>Задание выполнено!</b>\n\n"
                f"💰 Вы уже знаете этот рецепт, поэтому получаете {bonus_money} 🪙 вместо него!",
                parse_mode="HTML",
            )
        except Exception:
            pass
        save_data()
