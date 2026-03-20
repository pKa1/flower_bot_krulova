# effects.py

from datetime import datetime

from bot_instance import bot
from game_data import flower_combinations, growing_plant_water_time_minutes


def check_active_combinations(bouquets):
    """
    Возвращает список активных комбинаций по текущим букетам.
    Комбинация считается активной, если в каком-либо букете есть все её цветы.
    """
    active_combos = []

    for bouquet in bouquets:
        bouquet_flowers = bouquet.get("flowers", [])
        bouquet_id = bouquet.get("id", 0)

        for combo_name, combo_data in flower_combinations.items():
            required_flowers = combo_data["flowers"]
            # Все ли нужные цветы есть в букете
            if all(f in bouquet_flowers for f in required_flowers):
                active_combos.append(
                    {
                        "name": combo_name,
                        "flowers": required_flowers,
                        "effect": combo_data["effect"],
                        "effect_type": combo_data["effect_type"],
                        "effect_value": combo_data["effect_value"],
                        "description": combo_data["description"],
                        "bouquet_id": bouquet_id,
                    }
                )

    return active_combos


def get_combination_effects(bouquets):
    """
    Суммирует эффекты всех активных комбинаций по букетам.

    Возвращает:
      effects: словарь с суммарными значениями эффектов
      active_combos: список активных комбинаций (подробно)
    """
    active_combos = check_active_combinations(bouquets)

    effects = {
        "bonus_income": 0.0,    # множитель дохода
        "speed_growth": 0.0,    # ускорение роста
        "water_time": 0.0,      # увеличение времени до высыхания
        "water_interval": 0.0,  # увеличение интервала между поливами
        "bonus_money": 0,       # ежедневный бонус монет
    }

    for combo in active_combos:
        effect_type = combo["effect_type"]
        effect_value = combo["effect_value"]

        if effect_type == "bonus_income":
            effects["bonus_income"] += effect_value
        elif effect_type == "speed_growth":
            effects["speed_growth"] += effect_value
        elif effect_type == "water_time":
            effects["water_time"] += effect_value
        elif effect_type == "water_interval":
            effects["water_interval"] += effect_value
        elif effect_type == "bonus_money":
            effects["bonus_money"] += effect_value

    return effects, active_combos


def apply_income_bonus(base_income, bouquets):
    """
    Применяет бонус к доходу от комбинаций.
    Используется при начислении монет с выросших растений.
    """
    effects, _ = get_combination_effects(bouquets)
    bonus = effects["bonus_income"]
    return int(base_income * (1 + bonus))


def apply_growth_speed(bouquets, base_minutes):
    """
    Применяет ускорение роста от комбинаций.
    Возвращает новое время роста в минутах.
    """
    effects, _ = get_combination_effects(bouquets)
    speed_bonus = effects["speed_growth"]
    return int(base_minutes * (1 - speed_bonus))


def apply_water_time(bouquets, base_minutes=growing_plant_water_time_minutes):
    """
    Применяет увеличение времени до высыхания от комбинаций.
    Возвращает новое время до высыхания в минутах.
    """
    effects, _ = get_combination_effects(bouquets)
    time_bonus = effects["water_time"]
    return int(base_minutes * (1 + time_bonus))


def apply_water_interval(bouquets, base_hours=6):
    """
    Применяет увеличение интервала между поливами от комбинаций.
    Возвращает новое значение интервала в часах.
    """
    effects, _ = get_combination_effects(bouquets)
    interval_bonus = effects["water_interval"]
    return base_hours * (1 + interval_bonus)


def check_new_combinations(user_id: str, player: dict, previous_combos: list):
    """
    Проверяет, появились ли новые комбинации по сравнению с previous_combos,
    и отправляет игроку уведомления о новых комбинациях.
    """
    current_combos = check_active_combinations(player.get("bouquets", []))
    current_names = {c["name"] for c in current_combos}
    previous_names = {c["name"] for c in previous_combos}

    new_combos = [c for c in current_combos if c["name"] not in previous_names]

    for combo in new_combos:
        try:
            flowers_text = ", ".join(combo["flowers"])
            message = (
                "🎉 <b>Обнаружена новая комбинация!</b>\n\n"
                f"🌸 <b>{combo['name']}</b>\n"
                f"Цветы: {flowers_text}\n\n"
                f"✨ <b>Эффект:</b> {combo['effect']}\n"
                f"📝 {combo['description']}"
            )
            bot.send_message(int(user_id), message, parse_mode="HTML")
        except Exception:
            # чтобы бот не падал из-за ошибки отправки сообщения
            pass
