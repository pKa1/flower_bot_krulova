# services.py
from datetime import datetime, timedelta
import threading
import time
import random

from storage import players_data, save_data
from game_data import seeds_data, rarity_grow_time_minutes, rarity_grow_chance, growing_plant_water_time_minutes
from effects import apply_growth_speed, apply_water_time, apply_water_interval, apply_income_bonus, check_new_combinations, check_active_combinations
from bot_instance import bot
from quests import update_quest_progress


def is_plant_ready(plant_entry: dict, bouquets=None) -> bool:
    rarity = plant_entry.get("plant")
    planted_at_iso = plant_entry.get("planted_at")
    if not rarity or not planted_at_iso:
        return False

    try:
        planted_at = datetime.fromisoformat(planted_at_iso)
    except Exception:
        return False

    base_minutes = rarity_grow_time_minutes.get(rarity)
    if base_minutes is None:
        return False

    if bouquets:
        base_minutes = apply_growth_speed(bouquets, base_minutes)

    return datetime.now() >= planted_at + timedelta(minutes=base_minutes)


def growth_watcher_loop(check_interval_seconds: int = 60) -> None:
    while True:
        try:
            now = datetime.now()
            for user_id, pdata in list(players_data.items()):
                garden = pdata.get("garden", [])
                bouquets = pdata.get("bouquets", [])
                any_updates = False

                for plant_entry in list(garden):
                    if not plant_entry:
                        continue

                    # инициализация времени полива один раз
                    if "water_at" not in plant_entry:
                        plant_entry["water_at"] = now.isoformat()
                        any_updates = True

                    try:
                        water_at = datetime.fromisoformat(plant_entry["water_at"])
                    except Exception:
                        water_at = now
                        plant_entry["water_at"] = now.isoformat()
                        any_updates = True

                    time_since_water = now - water_at

                    # растение еще растет → контролируем высыхание
                    if not plant_entry.get("notified", False):
                        dry_minutes = apply_water_time(bouquets, growing_plant_water_time_minutes)
                        dry_delta = timedelta(minutes=dry_minutes)

                        if time_since_water > dry_delta:
                            garden.remove(plant_entry)
                            try:
                                bot.send_message(
                                    int(user_id),
                                    "💀 Растение засохло из-за недостатка воды!",
                                )
                            except Exception:
                                pass
                            any_updates = True
                            continue

                        warning_time = int(dry_minutes * 0.8)
                        warning_delta = timedelta(minutes=warning_time)

                        if (
                            time_since_water >= warning_delta
                            and not plant_entry.get("dry_warning_sent", False)
                        ):
                            plant_name = plant_entry.get("plant", "растение")
                            time_left = dry_delta - time_since_water
                            minutes_left = max(0, int(time_left.total_seconds() // 60))
                            seconds_left = max(0, int(time_left.total_seconds() % 60))

                            try:
                                if minutes_left > 0:
                                    bot.send_message(
                                        int(user_id),
                                        f"⚠️ <b>Внимание!</b> Растение {plant_name} "
                                        f"засохнет через {minutes_left}м {seconds_left}с! "
                                        "Срочно полейте его! 💧",
                                        parse_mode="HTML",
                                    )
                                else:
                                    bot.send_message(
                                        int(user_id),
                                        f"⚠️ <b>Внимание!</b> Растение {plant_name} "
                                        f"засохнет через {seconds_left}с! "
                                        "Срочно полейте его! 💧",
                                        parse_mode="HTML",
                                    )
                                plant_entry["dry_warning_sent"] = True
                                any_updates = True
                            except Exception:
                                pass

                        if plant_entry.get("dry_warning_sent") and time_since_water < warning_delta:
                            plant_entry["dry_warning_sent"] = False
                            any_updates = True

                    # растение уже выросло → начисляем доход
                    if plant_entry.get("notified") is True:
                        water_interval_hours = apply_water_interval(bouquets)
                        if time_since_water <= timedelta(hours=water_interval_hours):
                            flower_name = plant_entry.get("plant")
                            for rarity, flowers in seeds_data.items():
                                if flower_name in flowers:
                                    base_income = flowers[flower_name]["income"]
                                    income = apply_income_bonus(base_income, bouquets)
                                    pdata["money"] += income
                                    pdata["total_income"] += income
                                    update_quest_progress(user_id, "earn_money", income)
                                    any_updates = True
                                    break

                        try:
                            last_notif = datetime.fromisoformat(pdata["last_notification"])
                        except Exception:
                            last_notif = now
                            pdata["last_notification"] = now.isoformat()

                        if now - last_notif >= timedelta(minutes=60) and pdata["total_income"] > 0:
                            try:
                                bot.send_message(
                                    int(user_id),
                                    f"Поздравляем! Вам начислено за ваш сад "
                                    f"<b>{pdata['total_income']} 🪙!</b>",
                                    parse_mode="HTML",
                                )
                            except Exception:
                                pass
                            pdata["last_notification"] = now.isoformat()
                            pdata["total_income"] = 0
                            any_updates = True

                    # проверка на готовность к росту
                    if is_plant_ready(plant_entry, bouquets):
                        rarity = plant_entry.get("plant")
                        new_rarity = random.choice(rarity_grow_chance[rarity])
                        flower_name = random.choice(list(seeds_data[new_rarity].keys()))
                        plant_entry["plant"] = flower_name
                        plant_entry["notified"] = True
                        plant_entry["water_at"] = now.isoformat()
                        any_updates = True

                        if "previous_combos" not in pdata:
                            pdata["previous_combos"] = []

                        check_new_combinations(user_id, pdata, pdata.get("previous_combos", []))
                        pdata["previous_combos"] = check_active_combinations(bouquets)

                        try:
                            bot.send_message(
                                int(user_id),
                                f"🌼 Растение {rarity} выросло! Выросла {flower_name}",
                            )
                        except Exception:
                            pass

                if any_updates:
                    save_data()

        except Exception:
            # защита от падения фонового потока
            pass

        time.sleep(check_interval_seconds)


def start_growth_watcher() -> None:
    thread = threading.Thread(
        target=growth_watcher_loop, kwargs={"check_interval_seconds": 60}, daemon=True
    )
    thread.start()
