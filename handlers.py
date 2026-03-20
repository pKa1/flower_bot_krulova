# handlers.py
#
# Все хендлеры бота.
# Предполагается, что остальная логика вынесена в модули:
# - bot_instance.py       -> bot
# - storage.py            -> players_data, save_data
# - utils.py              -> get_player_data, error_logger
# - game_data.py          -> seeds_data, seeds_price,
#                             rarity_grow_time_minutes,
#                             growing_plant_water_time_minutes
# - effects.py            -> get_combination_effects,
#                             apply_growth_speed,
#                             apply_water_time,
#                             apply_water_interval,
#                             check_active_combinations,
#                             check_new_combinations
# - quests.py             -> get_daily_quest, update_quest_progress
# - minigames.py          -> start_minigame_quiz,
#                             start_minigame_guess,
#                             complete_minigame
#
# Логика по сути остается прежней, код только разбит по файлам и слегка
# упрощены некоторые проверки.

from datetime import datetime, timedelta
import random

from telebot import types

from bot_instance import bot
from storage import players_data, save_data, ah_data
from utils import get_player_data, error_logger
from game_data import (
    seeds_data,
    seeds_price,
    rarity_grow_time_minutes,
    growing_plant_water_time_minutes,
)
from effects import (
    get_combination_effects,
    apply_growth_speed,
    apply_water_time,
    apply_water_interval,
    apply_income_bonus,
    check_active_combinations,
    check_new_combinations,
)
from quests import get_daily_quest, update_quest_progress
from minigames import start_minigame_quiz, start_minigame_guess, complete_minigame


# -----------------------------------------------------------------------------
# Вспомогательные тексты
# -----------------------------------------------------------------------------


def format_welcome_message() -> str:
    welcome_text = """
🌸 <b>Добро пожаловать в Цветочный Сад!</b> 🌸

🎮 <b>Добро пожаловать в удивительный мир цветов!</b> 

В этой игре вы станете настоящим садоводом и будете выращивать прекрасные цветы разных редкостей!

💰 <b>Валюта:</b> Монеты - зарабатывайте их, выращивая и продавая цветы

🌸 <b>Редкости цветов:</b>
⚪ Обычный - простые цветы, быстрый рост
🔵 Редкий - красивые цветы, хороший доход  
🟣 Эпический - уникальные цветы, высокий доход
🟡 Легендарный - самые редкие цветы, огромная прибыль!

🏡 <b>Ваш сад:</b> Начните с одной грядки, расширяйте сад по мере роста!

🏪 <b>Магазин:</b> Покупайте семена и продавайте готовые цветы

📊 <b>Рейтинг:</b> Соревнуйтесь с другими садоводами

🌸 <b>Комбинации цветов:</b> Создавайте букеты и добавляйте в них цветы из инвентаря, чтобы активировать мощные эффекты! Используйте /витрина для управления букетами и /combinations для просмотра активных комбинаций.

<b>🎯 Доступные команды:</b>
/start - Начать игру
/garden - Посмотреть сад
/shop - Открыть магазин
/inventory - Проверить инвентарь
/plant - Посадить семена
/harvest - Собрать урожай
/витрина - Управление букетами (комбинации)
/combinations - Просмотреть активные комбинации
/quest - Ежедневное задание
/minigame - Мини-игры (викторина или угадай число)
/recipes - Просмотреть рецепты комбинаций
/rating - Рейтинг игроков
/buy_garden - Купить дополнительную грядку
/help - Помощь

🌱 <b>Начните с посадки семян и создайте свой цветочный рай!</b>
"""
    return welcome_text

def format_return_message() -> str:
    return (
        "🌸 <b>С возвращением в Цветочный Сад!</b> 🌸\n\n"
        "Ваши цветы скучали. Продолжайте выращивание, собирайте урожай и усиливайте сад букетами.\n\n"
        "🏪 Используйте /shop для покупки семян\n"
        "🏡 Загляните в /garden, чтобы проверить грядки\n"
        "💐 Попробуйте /витрина для комбинаций и бонусов\n"
        "🎯 Загляните в /quest и /minigame, чтобы получить награды"
    )

# -----------------------------------------------------------------------------
# /start
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["start"])
def start(message):
    try:
        user_id = str(message.from_user.id)
        player, is_new = get_player_data(message, user_id)
        get_daily_quest(user_id)
        print(players_data)
        greeting = format_welcome_message() if is_new else format_return_message()

        # Ежедневный бонус от комбинаций
        if not is_new:
            effects, _ = get_combination_effects(player.get("bouquets", []))
            if effects["bonus_money"] > 0:
                last_bonus_date = player.get("last_bonus_date", "")
                today = datetime.now().date().isoformat()
                if last_bonus_date != today:
                    player["money"] += effects["bonus_money"]
                    player["last_bonus_date"] = today

        text = greeting + f"\n\n💰 <b>Ваш баланс:</b> {player['money']} 🪙"
        bot.send_message(message.chat.id, text, parse_mode="HTML")
        save_data()
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при запуске бота🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /inventory
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["inventory"])
def inventory_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        seeds = player["inventory"]["seeds"]
        flowers = player["inventory"]["flowers"]
        bonuses = player["inventory"]["bonuses"]

        text_lines = [
            "🎒 <b>Ваш инвентарь</b>\n",
            f"💰 <b>Монеты:</b> {player['money']} 🪙\n",
        ]

        if seeds:
            text_lines.append("\n🌱 <b>Семена:</b>")
            for rarity, count in seeds.items():
                text_lines.append(f"\n • {rarity} семена: {count} шт.")

        if flowers:
            text_lines.append("\n\n🌸 <b>Цветы:</b>")
            for name, count in flowers.items():
                text_lines.append(f"\n • {name}: {count} шт.")

        if bonuses:
            text_lines.append("\n\n🎁 <b>Бонусы:</b>")
            for bonus in bonuses:
                text_lines.append(f"\n • {bonus}")

        if not seeds and not flowers and not bonuses:
            text_lines.append("\n\nПока что инвентарь пуст. Зайдите в /shop!")

        bot.send_message(message.chat.id, "".join(text_lines), parse_mode="HTML")
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре инвентаря🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /shop + покупка/продажа
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["shop"])
def shop_command(message):
    try:
        user_id = str(message.from_user.id)
        get_player_data(message, user_id)

        shop_text = (
            "🏪 <b>Магазин</b>\n\n"
            "Здесь вы можете купить семена или продать цветы.\n\n"
            "<b>Выберите действие:</b>"
        )
        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                "Купить семена", callback_data="buy_seeds_shop"
            ),
            types.InlineKeyboardButton(
                "Продать цветы", callback_data="sell_flowers"
            ),
        )
        bot.send_message(
            message.chat.id, shop_text, parse_mode="HTML", reply_markup=kb
        )
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре магазина🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "sell_flowers")
def sell_flowers_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        flowers = player["inventory"]["flowers"]
        if not flowers:
            bot.send_message(
                call.message.chat.id,
                "🌸 У вас нет цветов для продажи.",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        text = "💐 <b>Продажа цветов</b>\n\nВыберите цветок для продажи:\n"
        for name, count in flowers.items():
            # ищем цену в seeds_data
            price = 0
            for rarity, f_data in seeds_data.items():
                if name in f_data:
                    price = f_data[name]["price"]
                    break
            kb.row(
                types.InlineKeyboardButton(
                    f"{name} ({count} шт.) - {price} 🪙",
                    callback_data=f"sell_flower_{name}",
                )
            )

        bot.send_message(
            call.message.chat.id, text, parse_mode="HTML", reply_markup=kb
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при продаже цветов🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("sell_flower_"))
def sell_flower_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        flower = call.data.split("_", 2)[2]
        flowers_inv = player["inventory"]["flowers"]

        if flowers_inv.get(flower, 0) <= 0:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет такого цветка для продажи.",
                parse_mode="HTML",
            )
            return

        price = 0
        for rarity, f_data in seeds_data.items():
            if flower in f_data:
                price = f_data[flower]["price"]
                break

        player["money"] += price
        flowers_inv[flower] -= 1
        if flowers_inv[flower] <= 0:
            del flowers_inv[flower]

        bot.send_message(
            call.message.chat.id,
            f"💰 Вы продали {flower} за {price} 🪙",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при продаже цветка🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "buy_seeds_shop")
def buy_seeds_shop_callback(call):
    """Меню выбора редкости семян"""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        kb = types.InlineKeyboardMarkup()
        text = (
            "🏪 <b>Покупка семян</b>\n"
            f"💰 Ваш баланс: {player['money']} 🪙\n\n"
            "Выберите редкость семян:"
        )

        for rarity in seeds_price:
            kb.row(
                types.InlineKeyboardButton(
                    f"{rarity} ({seeds_price[rarity]} 🪙)",
                    callback_data=f"buy_seeds_{rarity}",
                )
            )

        bot.send_message(
            call.message.chat.id, text, parse_mode="HTML", reply_markup=kb
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при открытии покупки семян🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_seeds_"))
def buy_seeds_callback(call):
    """Непосредственная покупка семян выбранной редкости"""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)

        rarity = call.data.split("_", 2)[2]
        price = seeds_price[rarity]

        if player["money"] < price:
            bot.send_message(
                call.message.chat.id,
                f"❌ У вас недостаточно монет! Нужно: {price} 🪙, у вас: {player['money']} 🪙",
                parse_mode="HTML",
            )
            return

        player["money"] -= price
        seeds_inv = player["inventory"]["seeds"]
        seeds_inv[rarity] = seeds_inv.get(rarity, 0) + 1

        update_quest_progress(user_id, "buy_seeds_count", 1)

        bot.send_message(
            call.message.chat.id,
            f"🏪 Вы купили семена редкости {rarity} за {price} 🪙",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при покупке семян🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /plant + посадка
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["plant"])
def plant_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        if not player["inventory"]["seeds"]:
            bot.send_message(
                message.chat.id,
                "🏪 У вас нет семян для посадки. Купите их в /shop",
                parse_mode="HTML",
            )
            return

        if len(player["garden"]) >= player.get("max_garden", 5):
            bot.send_message(
                message.chat.id,
                f"🏡 У вас не хватает места в саду.\n"
                f"Максимум грядок: {player.get('max_garden', 5)}",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        for rarity, count in player["inventory"]["seeds"].items():
            kb.row(
                types.InlineKeyboardButton(
                    f"{rarity} семена ({count} шт.)",
                    callback_data=f"plant_rarity:{rarity}",
                )
            )

        bot.send_message(
            message.chat.id,
            "🌱 Выберите семена для посадки:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при посадке семян🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("plant_rarity:"))
def plant_rarity_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        rarity = call.data.split(":", 1)[1]
        seeds_inv = player["inventory"]["seeds"]

        if seeds_inv.get(rarity, 0) <= 0:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет таких семян.",
                parse_mode="HTML",
            )
            return

        if len(player["garden"]) >= player.get("max_garden", 5):
            bot.send_message(
                call.message.chat.id,
                f"🏡 У вас не хватает места в саду.\nМаксимум грядок: {player.get('max_garden', 5)}",
                parse_mode="HTML",
            )
            return

        seeds_inv[rarity] -= 1
        if seeds_inv[rarity] <= 0:
            del seeds_inv[rarity]

        new_bed = {
            "plant": rarity,  # пока редкость, потом вырастет в конкретный цветок
            "planted_at": datetime.now().isoformat(),
            "notified": False,
            "water_at": datetime.now().isoformat(),
            "dry_warning_sent": False,
        }
        player["garden"].append(new_bed)

        update_quest_progress(user_id, "plant_count", 1)

        bot.send_message(
            call.message.chat.id,
            f"🌱 Вы посадили семена редкости {rarity}!",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при посадке семян🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /harvest + сбор
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["harvest"])
def harvest_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        kb = types.InlineKeyboardMarkup()
        has_ready = False
        for i, bed in enumerate(player["garden"], 1):
            if bed.get("notified") is True:
                has_ready = True
                kb.row(
                    types.InlineKeyboardButton(
                        f"Грядка {i}: {bed['plant']}",
                        callback_data=f"harvest_bed:{i}",
                    )
                )

        if not has_ready:
            bot.send_message(
                message.chat.id,
                "🌱 Пока нет растений, готовых к сбору.",
                parse_mode="HTML",
            )
            return

        bot.send_message(
            message.chat.id,
            "🏪 Выберите грядку для сбора урожая:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при сборе урожая🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("harvest_bed:"))
def harvest_bed_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bed_index = int(call.data.split(":", 1)[1]) - 1
        if bed_index < 0 or bed_index >= len(player["garden"]):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный номер грядки.",
                parse_mode="HTML",
            )
            return

        bed = player["garden"][bed_index]
        if not bed.get("notified", False):
            bot.send_message(
                call.message.chat.id,
                "❌ Растение на этой грядке ещё не выросло.",
                parse_mode="HTML",
            )
            return

        flower_name = bed.get("plant")
        flowers_inv = player["inventory"]["flowers"]
        flowers_inv[flower_name] = flowers_inv.get(flower_name, 0) + 1

        player["garden"].pop(bed_index)

        update_quest_progress(user_id, "harvest_count", 1)

        bot.send_message(
            call.message.chat.id,
            f"🌸 Вы собрали урожай: {flower_name} перенесён в инвентарь.",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при сборе урожая🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /garden + /water
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["garden"])
def garden_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        if not player["garden"]:
            bot.send_message(
                message.chat.id,
                "🌱 У вас пока ничего не посажено.",
                parse_mode="HTML",
            )
            return

        bouquets = player.get("bouquets", [])
        active_combos = check_active_combinations(bouquets)
        effects, _ = get_combination_effects(bouquets)

        text = "🌱 <b>Ваш сад:</b>\n\n"

        if active_combos:
            text += (
                f"✨ <b>Активные комбинации (из букетов):</b> {len(active_combos)}\n"
            )
            if effects["bonus_income"] > 0:
                text += f"💰 Бонус дохода: +{int(effects['bonus_income'] * 100)}% | "
            if effects["speed_growth"] > 0:
                text += f"⚡ Рост: +{int(effects['speed_growth'] * 100)}% | "
            if effects["water_time"] > 0:
                text += f"💧 Защита: +{int(effects['water_time'] * 100)}%\n"
            text += "\n"

        now = datetime.now()

        for i, bed in enumerate(player["garden"], 1):
            plant_name = bed.get("plant", "неизвестно")

            # Время полива
            try:
                water_at = datetime.fromisoformat(
                    bed.get("water_at", now.isoformat())
                )
            except Exception:
                water_at = now
                bed["water_at"] = now.isoformat()
            time_since_water = now - water_at

            text += f"Грядка {i}: {plant_name}\n"

            if bed.get("notified", False):
                # Растение выросло
                income = 0
                for rarity, flowers in seeds_data.items():
                    if plant_name in flowers:
                        income = flowers[plant_name]["income"]
                        break

                income = apply_income_bonus(income, bouquets)

                water_interval_hours = apply_water_interval(bouquets, 6)
                time_until_dry = (
                    timedelta(hours=water_interval_hours) - time_since_water
                )

                text += "  🌸 Растение выросло!\n"
                text += f"  💰 Доход: {income} 🪙 в минуту\n"

                if time_until_dry.total_seconds() > 0:
                    minutes_left = int(time_until_dry.total_seconds() / 60)
                    h = minutes_left // 60
                    m = minutes_left % 60
                    if h > 0:
                        text += f"  💧 Полив через: {h}ч {m}м\n"
                    else:
                        text += f"  💧 Полив через: {m}м\n"
                else:
                    text += "  💀 Растение скоро засохнет без полива!\n"
            else:
                # Растение растет
                rarity = plant_name
                grow_minutes = rarity_grow_time_minutes.get(rarity, 10)
                grow_minutes = apply_growth_speed(bouquets, grow_minutes)

                try:
                    planted_at = datetime.fromisoformat(
                        bed.get("planted_at", now.isoformat())
                    )
                    elapsed = now - planted_at
                except Exception:
                    planted_at = now
                    bed["planted_at"] = now.isoformat()
                    elapsed = timedelta(0)

                total_grow = timedelta(minutes=grow_minutes)
                remaining = total_grow - elapsed

                if remaining.total_seconds() <= 0:
                    text += "  ⏱ Готово к сбору (обновите /garden)\n"
                else:
                    minutes_left = int(remaining.total_seconds() / 60)
                    h = minutes_left // 60
                    m = minutes_left % 60
                    if h > 0:
                        text += f"  ⏱ До роста: {h}ч {m}м\n"
                        text += f"  💰 Начнет приносить доход через: {h}ч {m}м\n"
                    else:
                        text += f"  ⏱ До роста: {m}м\n"
                        text += f"  💰 Начнет приносить доход через: {m}м\n"

                # Информация о высыхании (для растущего)
                dry_minutes = apply_water_time(
                    bouquets, growing_plant_water_time_minutes
                )
                dry_delta = timedelta(minutes=dry_minutes)
                dry_remaining = dry_delta - time_since_water
                if dry_remaining.total_seconds() > 0:
                    minutes_left = int(dry_remaining.total_seconds() / 60)
                    h = minutes_left // 60
                    m = minutes_left % 60
                    if h > 0:
                        text += f"  💧 До высыхания: {h}ч {m}м\n"
                    else:
                        text += f"  💧 До высыхания: {m}м\n"
                else:
                    text += "  💀 Скоро засохнет без полива!\n"

            text += "\n"

        save_data()
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре сада🤯",
            parse_mode="HTML",
        )


@bot.message_handler(commands=["water"])
def water_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        if not player["garden"]:
            bot.send_message(
                message.chat.id,
                "🌱 В саду нет растений для полива.",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        for i, bed in enumerate(player["garden"], 1):
            plant_name = bed.get("plant", "неизвестно")
            kb.row(
                types.InlineKeyboardButton(
                    f"Грядка {i}: {plant_name}",
                    callback_data=f"water_bed:{i}",
                )
            )
        
        # Добавляем кнопку "Полить всё"
        kb.row(
            types.InlineKeyboardButton(
                "💧 Полить всё",
                callback_data="water_all"
            )
        )

        bot.send_message(
            message.chat.id,
            "💧 Выберите грядку для полива:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при выборе грядки для полива🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "water_all")
def water_all_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        if not player["garden"]:
            bot.send_message(
                call.message.chat.id,
                "🌱 В саду нет растений для полива.",
                parse_mode="HTML",
            )
            return

        now_str = datetime.now().isoformat()
        count = len(player["garden"])
        
        for bed in player["garden"]:
            bed["water_at"] = now_str
            bed["dry_warning_sent"] = False

        update_quest_progress(user_id, "water_count", count)
        save_data()

        bot.send_message(
            call.message.chat.id,
            f"💧 Все растения (<b>{count}</b> шт.) успешно политы!",
            parse_mode="HTML",
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при массовом поливе🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("water_bed:"))
def water_bed_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bed_index = int(call.data.split(":", 1)[1]) - 1
        if bed_index < 0 or bed_index >= len(player["garden"]):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный номер грядки.",
                parse_mode="HTML",
            )
            return

        bed = player["garden"][bed_index]
        bed["water_at"] = datetime.now().isoformat()
        bed["dry_warning_sent"] = False

        update_quest_progress(user_id, "water_count", 1)

        bot.send_message(
            call.message.chat.id,
            "💧 Растение полито!",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при поливе растения🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /quest
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["quest", "daily"])
def quest_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        quest = get_daily_quest(user_id)
        if not quest:
            bot.send_message(
                message.chat.id,
                "❌ Не удалось получить задание.",
                parse_mode="HTML",
            )
            return

        quest_type = quest["type"]
        progress = player.get("quest_progress", {}).get(quest_type, 0)
        target = quest["target"]
        completed = quest.get("completed", False) or progress >= target

        text = "📋 <b>Ежедневное задание</b>\n\n"
        text += f"🎯 <b>{quest['name']}</b>\n"
        text += f"📝 {quest['description']}\n\n"

        if completed:
            text += "✅ <b>Задание выполнено!</b>\n"
            if quest.get("completed", False):
                text += "🎁 Награда уже получена!"
            else:
                text += "🎁 Награда будет выдана автоматически!"
        else:
            progress_percent = min(int((progress / target) * 10), 10)
            bar = "█" * progress_percent + "░" * (10 - progress_percent)
            text += f"📊 Прогресс: {progress}/{target}\n"
            text += bar + "\n\n"
            text += "🎁 <b>Награда:</b> Рецепт случайной комбинации!"

        text += "\n\n━━━━━━━━━━━━━━━━━━━\n"
        text += "💡 <b>Совет:</b> выполняйте задания каждый день, чтобы получать новые рецепты комбинаций!"

        bot.send_message(message.chat.id, text, parse_mode="HTML")
        save_data()
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре задания🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /minigame + мини-игры
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["minigame"])
def minigame_command(message):
    try:
        user_id = str(message.from_user.id)
        get_player_data(message, user_id)

        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                "❓ Викторина", callback_data="minigame_quiz"
            )
        )
        kb.row(
            types.InlineKeyboardButton(
                "🔢 Угадай число", callback_data="minigame_guess"
            )
        )

        text = (
            "🎮 <b>Мини-игры</b>\n\n"
            "Выберите игру:\n"
            "❓ Викторина — ответьте на вопрос\n"
            "🔢 Угадай число — попробуйте угадать число от 1 до 100"
        )

        bot.send_message(
            message.chat.id, text, parse_mode="HTML", reply_markup=kb
        )
        save_data()
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при запуске мини-игры🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "minigame_quiz")
def minigame_quiz_callback(call):
    try:
        user_id = str(call.from_user.id)
        question = start_minigame_quiz(user_id)

        if not question:
            bot.send_message(call.message.chat.id, "❌ Викторину можно пройти только один раз в день.", parse_mode="HTML")
            return

        kb = types.InlineKeyboardMarkup()
        for idx, option in enumerate(question["options"]):
            kb.row(
                types.InlineKeyboardButton(
                    option, callback_data=f"quiz_answer_{idx}"
                )
            )

        text = f"❓ <b>Викторина</b>\n\n{question['question']}"
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при запуске викторины🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "minigame_guess")
def minigame_guess_callback(call):
    try:
        user_id = str(call.from_user.id)
        minigame_state = start_minigame_guess(user_id)

        if not minigame_state:
            bot.send_message(call.message.chat.id, "❌ Игру 'Угадай число' можно играть только один раз в день.", parse_mode="HTML")
            return

        bot.edit_message_text(
            "🔢 <b>Игра 'Угадай число'</b>\n\n"
            "Я загадал число от 1 до 100.\n"
            "Отправьте число одним сообщением.\n"
            f"У вас {minigame_state['max_attempts']} попыток!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при запуске игры 'Угадай число'🤯",
            parse_mode="HTML",
        )


@bot.message_handler(func=lambda message: message.text and not message.text.startswith("/"))
def guess_number_handler(message):
    """Обработчик игры 'Угадай число'."""
    try:
        user_id = str(message.from_user.id)
        player = players_data.get(user_id)

        if not player or "minigame" not in player:
            return

        minigame = player["minigame"]
        if minigame.get("type") != "guess":
            return

        try:
            guessed_number = int(message.text.strip())
        except ValueError:
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите число от 1 до 100!",
                parse_mode="HTML",
            )
            return

        if not 1 <= guessed_number <= 100:
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите число от 1 до 100!",
                parse_mode="HTML",
            )
            return

        secret_number = minigame["secret_number"]
        attempts = minigame["attempts"] + 1
        minigame["attempts"] = attempts
        max_attempts = minigame["max_attempts"]

        if guessed_number == secret_number:
            complete_minigame(user_id, True)
            bot.send_message(
                message.chat.id,
                f"🎉 Вы угадали число {secret_number} за {attempts} попыток!",
                parse_mode="HTML",
            )
            save_data()
        else:
            if attempts >= max_attempts:
                complete_minigame(user_id, False)
                bot.send_message(
                    message.chat.id,
                    f"❌ Вы не угадали число за {max_attempts} попыток.\n"
                    f"Загаданное число было: {secret_number}.",
                    parse_mode="HTML",
                )
                save_data()
            else:
                if guessed_number < secret_number:
                    hint = "🔺 Загаданное число <b>больше</b>!"
                else:
                    hint = "🔻 Загаданное число <b>меньше</b>!"

                bot.send_message(
                    message.chat.id,
                    f"{hint}\n\n"
                    f"Попытка {attempts}/{max_attempts}\n\n"
                    "💡 Попробуйте еще раз!",
                    parse_mode="HTML",
                )
                save_data()
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz_answer_"))
def quiz_answer_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)

        if "minigame" not in player:
            bot.send_message(
                call.message.chat.id,
                "❌ Мини-игра не запущена!",
                parse_mode="HTML",
            )
            return

        minigame = player["minigame"]
        if minigame.get("type") != "quiz":
            bot.send_message(
                call.message.chat.id,
                "❌ Сейчас запущена другая мини-игра.",
                parse_mode="HTML",
            )
            return

        q = minigame["question"]
        correct_index = q["correct"]
        chosen_index = int(call.data.split("_")[-1])

        is_correct = chosen_index == correct_index
        complete_minigame(user_id, is_correct)

        if is_correct:
            msg = "🎉 Правильно! Награда выдана."
        else:
            msg = (
                "❌ Неправильно.\n"
                f"Правильный ответ: <b>{q['options'][correct_index]}</b>."
            )

        bot.edit_message_text(
            msg,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при проверке ответа🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /recipes
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["recipes"])
def recipes_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        recipes = player.get("recipes", [])
        if not recipes:
            bot.send_message(
                message.chat.id,
                "📜 У вас пока нет рецептов комбинаций.\n"
                "Получайте их за ежедневные задания и мини-игры!",
                parse_mode="HTML",
            )
            return

        text = "📜 <b>Ваши рецепты комбинаций</b>\n\n"
        for recipe in recipes:
            flowers = ", ".join(recipe["flowers"])
            text += f"• <b>{recipe['name']}</b>\n"
            text += f"  🌸 Цветы: {flowers}\n"
            text += f"  ✨ Эффект: {recipe['effect']}\n"
            text += f"  📝 {recipe['description']}\n\n"

        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре рецептов🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /combinations
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["combinations"])
def combinations_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        bouquets = player.get("bouquets", [])
        active_combos = check_active_combinations(bouquets)
        effects, _ = get_combination_effects(bouquets)

        if not active_combos:
            text = (
                "🌸 <b>Активные комбинации</b>\n\n"
                "У вас пока нет активных комбинаций цветов.\n\n"
                "💡 <b>Подсказка:</b> создайте букет и добавьте в него цветы "
                "из одной комбинации, чтобы активировать эффект! Используйте /витрина."
            )
            bot.send_message(message.chat.id, text, parse_mode="HTML")
            return

        text = "🌸 <b>Активные комбинации</b>\n\n"
        text += f"✨ <b>Всего активных комбинаций:</b> {len(active_combos)}\n\n"

        for combo in active_combos:
            flowers = ", ".join(combo["flowers"])
            text += f"• <b>{combo['name']}</b>\n"
            text += f"  🌸 Цветы: {flowers}\n"
            text += f"  ✨ Эффект: {combo['effect']}\n"
            text += f"  📝 {combo['description']}\n\n"

        text += "━━━━━━━━━━━━━━━━━━━\n"
        text += "💡 <b>Сводка эффектов:</b>\n"
        if effects["bonus_income"] > 0:
            text += f"💰 Бонус дохода: +{int(effects['bonus_income'] * 100)}%\n"
        if effects["speed_growth"] > 0:
            text += f"⚡ Скорость роста: +{int(effects['speed_growth'] * 100)}%\n"
        if effects["water_time"] > 0:
            text += f"💧 Время до высыхания: +{int(effects['water_time'] * 100)}%\n"
        if effects["water_interval"] > 0:
            text += (
                f"💧 Интервал между поливами: +{int(effects['water_interval'] * 100)}%\n"
            )
        if effects["bonus_money"] > 0:
            text += f"🎁 Ежедневный бонус монет: +{effects['bonus_money']} 🪙\n"

        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре комбинаций🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /витрина (showcase) + работа с букетами
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["витрина", "showcase"])
def showcase_command(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        bouquets = player.get("bouquets", [])
        max_bouquets = player.get("max_bouquets", 1)

        text = "💐 <b>Витрина букетов</b>\n\n"
        text += f"📦 Букетов: {len(bouquets)}/{max_bouquets}\n\n"

        if bouquets:
            text += "Ваши букеты:\n"
            for i, b in enumerate(bouquets, 1):
                flowers = ", ".join(b.get("flowers", [])) or "пусто"
                text += f"{i}. <b>{b.get('name', f'Букет {i}')}</b>: {flowers}\n"
            text += "\n"
        else:
            text += "У вас пока нет букетов.\n\n"

        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                "➕ Создать букет", callback_data="bouquet_create"
            )
        )
        if bouquets:
            kb.row(
                types.InlineKeyboardButton(
                    "✏️ Редактировать букет", callback_data="bouquet_edit_list"
                )
            )
            kb.row(
                types.InlineKeyboardButton(
                    "🗑 Удалить букет", callback_data="bouquet_delete_list"
                )
            )

        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при открытии витрины🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "bouquet_create")
def bouquet_create_callback(call):
    """Создание нового букета."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bouquets = player.get("bouquets", [])
        max_bouquets = player.get("max_bouquets", 1)

        if len(bouquets) >= max_bouquets:
            bot.send_message(
                call.message.chat.id,
                f"❌ Достигнут максимум букетов ({max_bouquets})!",
                parse_mode="HTML",
            )
            return

        existing_ids = [b.get("id", 0) for b in bouquets] if bouquets else []
        new_id = max(existing_ids) + 1 if existing_ids else 1

        new_bouquet = {
            "id": new_id,
            "name": f"Букет {len(bouquets) + 1}",
            "flowers": [],
        }
        bouquets.append(new_bouquet)
        player["bouquets"] = bouquets
        save_data()

        bot.send_message(
            call.message.chat.id,
            f"💐 Новый букет создан: <b>{new_bouquet['name']}</b>.",
            parse_mode="HTML",
        )
        showcase_command(call.message)
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при создании букета🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "bouquet_edit_list")
def bouquet_edit_list_callback(call):
    """Выбор букета для редактирования."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bouquets = player.get("bouquets", [])
        if not bouquets:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет букетов для редактирования.",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        for i, b in enumerate(bouquets, 1):
            kb.row(
                types.InlineKeyboardButton(
                    f"{i}. {b.get('name', f'Букет {i}')}",
                    callback_data=f"bouquet_edit_{i}",
                )
            )
        kb.row(
            types.InlineKeyboardButton(
                "⬅ Назад", callback_data="showcase_back"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "Выберите букет для редактирования:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при выборе букета🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("bouquet_edit_"))
def bouquet_edit_callback(call):
    """Меню редактирования конкретного букета."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        index = int(call.data.split("_")[-1]) - 1
        bouquets = player.get("bouquets", [])
        if index < 0 or index >= len(bouquets):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный букет.",
                parse_mode="HTML",
            )
            return

        bouquet = bouquets[index]
        flowers = ", ".join(bouquet.get("flowers", [])) or "пусто"

        text = f"💐 <b>{bouquet.get('name', f'Букет {index+1}')}</b>\n"
        text += f"🌸 Цветы: {flowers}\n\n"
        text += "Выберите действие:"

        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                "➕ Добавить цветок",
                callback_data=f"bouquet_add_flower_{index}",
            )
        )
        kb.row(
            types.InlineKeyboardButton(
                "➖ Удалить цветок",
                callback_data=f"bouquet_remove_flower_{index}",
            )
        )
        kb.row(
            types.InlineKeyboardButton(
                "⬅ Назад", callback_data="showcase_back"
            )
        )

        bot.send_message(
            call.message.chat.id, text, parse_mode="HTML", reply_markup=kb
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при редактировании букета🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("bouquet_add_flower_"))
def bouquet_add_flower_callback(call):
    """Выбор цветка для добавления в букет."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        index = int(call.data.split("_")[-1])
        bouquets = player.get("bouquets", [])
        if index < 0 or index >= len(bouquets):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный букет.",
                parse_mode="HTML",
            )
            return

        flowers_inv = player["inventory"]["flowers"]
        if not flowers_inv:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет цветов в инвентаре для добавления.",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        for name, count in flowers_inv.items():
            kb.row(
                types.InlineKeyboardButton(
                    f"{name} ({count} шт.)",
                    callback_data=f"bouquet_add_{index}_{name}",
                )
            )
        kb.row(
            types.InlineKeyboardButton(
                "⬅ Назад", callback_data="showcase_back"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "Выберите цветок для добавления в букет:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при выборе цветка🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("bouquet_add_"))
def bouquet_add_confirm_callback(call):
    """Подтверждение добавления цветка."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        parts = call.data.split("_")
        index = int(parts[2])
        flower_name = "_".join(parts[3:])

        bouquets = player.get("bouquets", [])
        if index < 0 or index >= len(bouquets):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный букет.",
                parse_mode="HTML",
            )
            return

        flowers_inv = player["inventory"]["flowers"]
        if flowers_inv.get(flower_name, 0) <= 0:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет такого цветка.",
                parse_mode="HTML",
            )
            return

        bouquet = bouquets[index]
        bouquet.setdefault("flowers", []).append(flower_name)
        flowers_inv[flower_name] -= 1
        if flowers_inv[flower_name] <= 0:
            del flowers_inv[flower_name]

        # Проверяем новые комбинации
        if "previous_combos" not in player:
            player["previous_combos"] = []
        check_new_combinations(user_id, player, player["previous_combos"])
        player["previous_combos"] = check_active_combinations(
            player.get("bouquets", [])
        )

        bot.send_message(
            call.message.chat.id,
            f"✅ Цветок {flower_name} добавлен в букет.",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при добавлении цветка в букет🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("bouquet_remove_flower_"))
def bouquet_remove_flower_callback(call):
    """Выбор цветка для удаления из букета."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        index = int(call.data.split("_")[-1])
        bouquets = player.get("bouquets", [])
        if index < 0 or index >= len(bouquets):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный букет.",
                parse_mode="HTML",
            )
            return

        bouquet = bouquets[index]
        bouquet_flowers = bouquet.get("flowers", [])
        if not bouquet_flowers:
            bot.send_message(
                call.message.chat.id,
                "❌ В этом букете нет цветов.",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        for i, name in enumerate(bouquet_flowers, 1):
            kb.row(
                types.InlineKeyboardButton(
                    f"{i}. {name}",
                    callback_data=f"bouquet_remove_{index}_{i-1}",
                )
            )
        kb.row(
            types.InlineKeyboardButton(
                "⬅ Назад", callback_data="showcase_back"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "Выберите цветок для удаления:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при выборе цветка для удаления🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("bouquet_remove_"))
def bouquet_remove_confirm_callback(call):
    """Подтверждение удаления цветка из букета."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        parts = call.data.split("_")
        index = int(parts[2])
        flower_index = int(parts[3])

        bouquets = player.get("bouquets", [])
        if index < 0 or index >= len(bouquets):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный букет.",
                parse_mode="HTML",
            )
            return

        bouquet = bouquets[index]
        bouquet_flowers = bouquet.get("flowers", [])
        if not (0 <= flower_index < len(bouquet_flowers)):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный цветок.",
                parse_mode="HTML",
            )
            return

        flower_name = bouquet_flowers.pop(flower_index)
        flowers_inv = player["inventory"]["flowers"]
        flowers_inv[flower_name] = flowers_inv.get(flower_name, 0) + 1

        # Пересчитваем комбинации
        if "previous_combos" not in player:
            player["previous_combos"] = []
        check_new_combinations(user_id, player, player["previous_combos"])
        player["previous_combos"] = check_active_combinations(
            player.get("bouquets", [])
        )

        bot.send_message(
            call.message.chat.id,
            f"✅ Цветок {flower_name} удален из букета и возвращен в инвентарь.",
            parse_mode="HTML",
        )
        save_data()
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при удалении цветка из букета🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "bouquet_delete_list")
def bouquet_delete_list_callback(call):
    """Выбор букета для удаления."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bouquets = player.get("bouquets", [])
        if not bouquets:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет букетов для удаления.",
                parse_mode="HTML",
            )
            return

        kb = types.InlineKeyboardMarkup()
        for i, b in enumerate(bouquets, 1):
            kb.row(
                types.InlineKeyboardButton(
                    f"Удалить {i}. {b.get('name', f'Букет {i}')}",
                    callback_data=f"bouquet_delete_{i}",
                )
            )
        kb.row(
            types.InlineKeyboardButton(
                "⬅ Назад", callback_data="showcase_back"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "Выберите букет для удаления:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при выборе букета для удаления🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("bouquet_delete_"))
def bouquet_delete_confirm_callback(call):
    """Подтверждение удаления букета."""
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        index = int(call.data.split("_")[-1]) - 1
        bouquets = player.get("bouquets", [])
        if index < 0 or index >= len(bouquets):
            bot.send_message(
                call.message.chat.id,
                "❌ Неверный букет.",
                parse_mode="HTML",
            )
            return

        deleted = bouquets.pop(index)
        player["bouquets"] = bouquets
        save_data()

        bot.send_message(
            call.message.chat.id,
            f"🗑 Букет <b>{deleted.get('name', 'без названия')}</b> удален.",
            parse_mode="HTML",
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при удалении букета🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "showcase_back")
def showcase_back_callback(call):
    """Возврат к витрине."""
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        showcase_command(call.message)
    except Exception:
        pass


# -----------------------------------------------------------------------------
# /rating
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["rating"])
def rating_command(message):
    try:
        user_id = str(message.from_user.id)
        get_player_data(message, user_id)

        if not players_data:
            bot.send_message(
                message.chat.id,
                "📊 Рейтинг пока пуст!",
                parse_mode="HTML",
            )
            return

        sorted_players = sorted(
            players_data.items(),
            key=lambda x: x[1].get("money", 0),
            reverse=True,
        )

        text = "🏆 <b>Рейтинг игроков</b> 🏆\n\n"
        text += "💰 <b>Топ по количеству монет:</b>\n\n"

        max_show = min(10, len(sorted_players))
        for i in range(max_show):
            pid, pdata = sorted_players[i]
            name = pdata.get("name", pid)
            money = pdata.get("money", 0)
            marker = " (вы)" if pid == user_id else ""
            text += f"{i+1}. {name}: {money} 🪙{marker}\n"

        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при просмотре рейтинга🤯",
            parse_mode="HTML",
        )


# -----------------------------------------------------------------------------
# /buy_garden + подтверждение покупки грядок
# -----------------------------------------------------------------------------


@bot.message_handler(commands=["buy_garden"])
def buy_max_gareden(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        current_max = player.get("max_garden", 5)
        base_price = 1271
        # прогрессивная цена: кубический рост после 5-й грядки
        garden_price = base_price * (current_max - 4) ** 3

        text = "🏡 <b>Расширение сада</b>\n\n"
        text += f"📊 <b>Текущее количество грядок:</b> {current_max}\n"
        text += f"💰 <b>Цена за новую грядку:</b> {garden_price} 🪙\n"
        text += f"💵 <b>Ваши монеты:</b> {player['money']} 🪙\n\n"

        if player["money"] >= garden_price:
            text += "Вы можете купить дополнительную грядку!"
            kb = types.InlineKeyboardMarkup()
            kb.row(
                types.InlineKeyboardButton(
                    "✅ Купить грядку", callback_data="buy_garden_confirm"
                )
            )
            kb.row(
                types.InlineKeyboardButton(
                    "❌ Отмена", callback_data="cancel"
                )
            )
            bot.send_message(
                message.chat.id, text, parse_mode="HTML", reply_markup=kb
            )
        else:
            text += f"❌ У вас недостаточно монет! Нужно: {garden_price} 🪙"
            bot.send_message(message.chat.id, text, parse_mode="HTML")

        save_data()
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при покупке грядки🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "buy_garden_confirm")
def buy_garden_confirm_callback(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        current_max = player.get("max_garden", 5)
        base_price = 1271
        garden_price = base_price * (current_max - 4) ** 3

        if player["money"] >= garden_price:
            player["money"] -= garden_price
            player["max_garden"] = current_max + 1
            bot.send_message(
                call.message.chat.id,
                "🎉 Поздравляем! Вы купили дополнительную грядку!\n\n"
                f"🏡 <b>Теперь грядок:</b> {player['max_garden']}\n"
                f"💰 <b>Потрачено:</b> {garden_price} 🪙",
                parse_mode="HTML",
            )
            save_data()
        else:
            bot.send_message(
                call.message.chat.id,
                f"❌ У вас недостаточно монет! Нужно: {garden_price} 🪙",
                parse_mode="HTML",
            )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при покупке грядки🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data == "back_to_ah")
def back_to_ah_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Подменяем message.from_user, чтобы ah_comand получил ID игрока, а не бота
        msg = call.message
        msg.from_user = call.from_user
        ah_comand(msg)
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)




@bot.message_handler(commands=["ah"])
def ah_comand(message):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)
        kb = types.InlineKeyboardMarkup()
        kb.row(
            types.InlineKeyboardButton(
                "🛒 Купить", callback_data="ah_buy"
            ),
            types.InlineKeyboardButton(
                "💰 Продать", callback_data="ah_sell"
            ),
        )
        kb.row(
            types.InlineKeyboardButton(
                "📦 Мои лоты", callback_data="ah_my_lots"
            )
        )
        bot.send_message(
            message.chat.id,
            "Это аукцион, где вы можете купить или продать свои растения.\n\nВыберите действие:",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при открытии аукциона🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("ah_my_lots"))
def ah_my_lots_command(call):
    try:
        user_id = str(call.from_user.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Пагинация
        page = 0
        if "_" in call.data:
            parts = call.data.split("_")
            if len(parts) > 3: # ah_my_lots_page_0
                page = int(parts[3])

        kb = types.InlineKeyboardMarkup()
        lots = ah_data.get("lots", [])
        
        # Фильтруем только свои лоты
        my_lots = [lot for lot in lots if str(lot["seller_id"]) == user_id]
        
        if not my_lots:
            kb.row(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_ah"))
            bot.send_message(
                call.message.chat.id,
                "📦 <b>У вас нет активных лотов на аукционе.</b>",
                parse_mode="HTML",
                reply_markup=kb
            )
            return

        items_per_page = 10
        total_pages = (len(my_lots) - 1) // items_per_page + 1
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_lots = my_lots[start_idx:end_idx]

        for lot in current_page_lots:
            amount_str = f" (x{lot['amount']})" if lot.get("amount", 1) > 1 else ""
            kb.row(
                types.InlineKeyboardButton(
                    f"❌ Снять #{lot['id']} | {lot['item_name']}{amount_str}",
                    callback_data=f"ah_remove_{lot['id']}"
                )
            )
        
        # Кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"ah_my_lots_page_{page-1}"))
        
        if total_pages > 1:
            nav_buttons.append(types.InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="ignore"))
            
        if end_idx < len(my_lots):
            nav_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"ah_my_lots_page_{page+1}"))
        
        if nav_buttons:
            kb.row(*nav_buttons)
            
        kb.row(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_ah"))

        bot.send_message(
            call.message.chat.id,
            f"📦 <b>Ваши лоты на продаже (Стр. {page + 1}):</b>\nНажмите на лот, чтобы снять его с продажи и вернуть предмет в инвентарь.",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(call.message.chat.id, "Произошла ошибка при открытии ваших лотов🤯")


@bot.callback_query_handler(func=lambda call: call.data.startswith("ah_remove_"))
def ah_remove_lot_callback(call):
    try:
        user_id = str(call.from_user.id)
        lot_id = call.data.replace("ah_remove_", "")
        
        lots = ah_data.get("lots", [])
        lot = next((l for l in lots if l["id"] == lot_id), None)
        
        if not lot:
            bot.answer_callback_query(call.id, "❌ Лот не найден.")
            return
            
        if str(lot["seller_id"]) != user_id:
            bot.answer_callback_query(call.id, "❌ Это не ваш лот!")
            return
            
        # Возвращаем предмет в инвентарь
        player, _ = get_player_data(call, user_id)
        if "inventory" not in player: player["inventory"] = {}
        if "flowers" not in player["inventory"]: player["inventory"]["flowers"] = {}
        
        flower_name = lot["item_name"]
        amount = lot.get("amount", 1)
        player["inventory"]["flowers"][flower_name] = player["inventory"]["flowers"].get(flower_name, 0) + amount
        
        # Удаляем лот
        ah_data["lots"].remove(lot)
        save_data()
        
        bot.answer_callback_query(call.id, f"✅ Лот #{lot_id} снят. {flower_name} (x{amount}) возвращен в инвентарь.")
        
        # Обновляем список лотов
        ah_my_lots_command(call)
        
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.answer_callback_query(call.id, "Произошла ошибка при снятии лота🤯")


@bot.callback_query_handler(func=lambda call: call.data == "ah_sell")
def ah_sell_command(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        kb = types.InlineKeyboardMarkup()

        flowers_inv = player.get("inventory", {}).get("flowers", {})
        if not flowers_inv:
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет растений для продажи.",
                parse_mode="HTML",
            )
            return

        for flower in flowers_inv:
            kb.row(
                types.InlineKeyboardButton(
                    f"{flower} ({flowers_inv[flower]} шт.)", callback_data=f"sell_ah_{flower}"
                )
            )
        
        kb.row(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_ah"))

        bot.send_message(
            call.message.chat.id,
            "Выберите растение для продажи:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при продаже на аукционе🤯",
            parse_mode="HTML",
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("sell_ah_"))
def sell_ah_flower(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)

        flower = call.data.replace("sell_ah_", "")
        if flower not in player.get("inventory", {}).get("flowers", {}):
            bot.send_message(
                call.message.chat.id,
                "❌ У вас нет этого растения для продажи.",
                parse_mode="HTML",
            )
            return

        msg = bot.send_message(
            call.message.chat.id,
            f"Введите цену, за которую вы хотите выставить <b>{flower}</b> на аукцион (за 1 шт.):",
            parse_mode="HTML"
        )
        bot.register_next_step_handler(msg, process_ah_price_step, flower)

    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при продаже на аукционе🤯",
            parse_mode="HTML",
        )


def process_ah_price_step(message, flower):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        try:
            price = int(message.text)
            if price <= 0:
                raise ValueError
        except ValueError:
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите корректное положительное число для цены.",
                parse_mode="HTML"
            )
            return

        flowers_inv = player.get("inventory", {}).get("flowers", {})
        max_amount = flowers_inv.get(flower, 0)

        if max_amount > 1:
            msg = bot.send_message(
                message.chat.id,
                f"У вас есть <b>{max_amount}</b> шт. <b>{flower}</b>. Сколько вы хотите выставить на продажу?",
                parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, process_ah_amount_step, flower, price)
        else:
            # Если цветок один, сразу выставляем
            finish_listing(message, flower, price, 1)

    except Exception as e:
        error_logger(message.from_user.username, message.text, e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при обработке цены🤯",
            parse_mode="HTML",
        )


def process_ah_amount_step(message, flower, price):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)

        try:
            amount = int(message.text)
            flowers_inv = player.get("inventory", {}).get("flowers", {})
            max_amount = flowers_inv.get(flower, 0)
            
            if amount <= 0 or amount > max_amount:
                bot.send_message(
                    message.chat.id,
                    f"❌ Введите корректное количество (от 1 до {max_amount}).",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            bot.send_message(
                message.chat.id,
                "❌ Пожалуйста, введите число.",
                parse_mode="HTML"
            )
            return

        finish_listing(message, flower, price, amount)

    except Exception as e:
        error_logger(message.from_user.username, message.text, e)


def finish_listing(message, flower, price, amount):
    try:
        user_id = str(message.from_user.id)
        player, _ = get_player_data(message, user_id)
        
        # Списываем цветы СРАЗУ при выставлении
        flowers_inv = player.get("inventory", {}).get("flowers", {})
        if flower not in flowers_inv or flowers_inv[flower] < amount:
            bot.send_message(
                message.chat.id,
                f"❌ Ошибка: у вас недостаточно растений {flower}.",
                parse_mode="HTML"
            )
            return

        flowers_inv[flower] -= amount
        if flowers_inv[flower] <= 0:
            del flowers_inv[flower]

        # Инициализируем данные аукциона
        if "lots" not in ah_data:
            ah_data["lots"] = []
        if "last_id" not in ah_data:
            # Если last_id нет, находим максимальный существующий ID
            if ah_data["lots"]:
                try:
                    ah_data["last_id"] = max(int(lot["id"]) for lot in ah_data["lots"])
                except:
                    ah_data["last_id"] = len(ah_data["lots"])
            else:
                ah_data["last_id"] = 0

        # Генерируем уникальный ID
        while True:
            ah_data["last_id"] += 1
            lot_id = str(ah_data["last_id"])
            # Проверяем, нет ли уже лота с таким ID
            if not any(lot["id"] == lot_id for lot in ah_data["lots"]):
                break
        
        new_lot = {
            "id": lot_id,
            "seller_id": user_id,
            "seller_username": message.from_user.username or message.from_user.first_name,
            "item_name": flower,
            "price": price,
            "amount": amount,
            "time": datetime.now().strftime("%d.%m.%Y %H:%M")
        }

        ah_data["lots"].append(new_lot)
        save_data()

        bot.send_message(
            message.chat.id,
            f"✅ Вы успешно выставили <b>{flower}</b> (x{amount}) на аукцион за <b>{price}</b> 💰 за шт.",
            parse_mode="HTML"
        )

    except Exception as e:
        error_logger(message.from_user.username, "listing_finish", e)
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при финальном выставлении лота🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("ah_buy"))
def ah_buy_command(call):
    try:
        user_id = str(call.from_user.id)
        player, _ = get_player_data(call, user_id)
        
        # Получаем номер страницы из callback_data (например, ah_buy_0)
        page = 0
        if "_" in call.data:
            parts = call.data.split("_")
            if len(parts) > 2:
                page = int(parts[2])

        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        kb = types.InlineKeyboardMarkup()
        lots = ah_data.get("lots", [])
        
        # Фильтруем лоты: убираем те, что принадлежат самому пользователю
        available_lots = [lot for lot in lots if lot["seller_id"] != user_id]
        
        if not available_lots:
            kb.row(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_ah"))
            bot.send_message(
                call.message.chat.id,
                "🛒 <b>Аукцион пуст</b>\n\nНа данный момент нет доступных товаров для покупки.",
                parse_mode="HTML",
                reply_markup=kb
            )
            return

        # Логика пагинации
        items_per_page = 10
        total_pages = (len(available_lots) - 1) // items_per_page + 1
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_lots = available_lots[start_idx:end_idx]

        for lot in current_page_lots:
            amount_str = f" (x{lot['amount']})" if lot.get("amount", 1) > 1 else ""
            kb.row(
                types.InlineKeyboardButton(
                    f"#{lot['id']} | {lot['seller_username']} | {lot['item_name']}{amount_str} - {lot['price']} 💰",
                    callback_data=f"buy_ah_{lot['id']}"
                )
            )
        
        # Кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"ah_buy_{page-1}"))
        
        nav_buttons.append(types.InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="ignore"))
        
        if end_idx < len(available_lots):
            nav_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"ah_buy_{page+1}"))
        
        kb.row(*nav_buttons)
        kb.row(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_ah"))
        
        bot.send_message(
            call.message.chat.id,
            f"<b>Список доступных лотов (Стр. {page + 1}):</b>",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.send_message(
            call.message.chat.id,
            "Произошла ошибка при открытии аукциона🤯",
            parse_mode="HTML",
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_ah_"))
def buy_ah_callback(call):
    try:
        user_id = str(call.from_user.id)
        buyer, _ = get_player_data(call, user_id)
        lot_id = call.data.replace("buy_ah_", "")
        
        lots = ah_data.get("lots", [])
        lot = next((l for l in lots if l["id"] == lot_id), None)
        
        if not lot:
            bot.answer_callback_query(call.id, "❌ Лот не найден или уже куплен.")
            return
        
        if str(lot["seller_id"]) == str(user_id):
            bot.answer_callback_query(call.id, "❌ Вы не можете купить собственный лот!")
            return
            
        amount_in_lot = lot.get("amount", 1)
        
        if amount_in_lot > 1:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            msg = bot.send_message(
                call.message.chat.id,
                f"В лоте <b>{lot['item_name']}</b> доступно <b>{amount_in_lot}</b> шт. по цене <b>{lot['price']}</b> 💰 за шт.\n"
                f"Сколько штук вы хотите купить?",
                parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, process_buy_amount_step, lot_id)
        else:
            # Если предмет один, сразу покупаем
            process_buy_final(call.message, lot_id, 1, call.from_user)

    except Exception as e:
        error_logger(call.from_user.username, call.data, e)
        bot.answer_callback_query(call.id, "Произошла ошибка при покупке🤯")


def process_buy_amount_step(message, lot_id):
    try:
        user_id = str(message.from_user.id)
        buyer, _ = get_player_data(message, user_id)
        
        lots = ah_data.get("lots", [])
        lot = next((l for l in lots if l["id"] == lot_id), None)
        
        if not lot:
            bot.send_message(message.chat.id, "❌ Лот больше не доступен.")
            return

        try:
            amount_to_buy = int(message.text)
            amount_in_lot = lot.get("amount", 1)
            
            if amount_to_buy <= 0 or amount_to_buy > amount_in_lot:
                bot.send_message(
                    message.chat.id,
                    f"❌ Введите корректное количество (от 1 до {amount_in_lot}).",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            bot.send_message(message.chat.id, "❌ Пожалуйста, введите число.", parse_mode="HTML")
            return

        process_buy_final(message, lot_id, amount_to_buy, message.from_user)

    except Exception as e:
        error_logger(message.from_user.username, "buy_amount_step", e)


def process_buy_final(message, lot_id, amount_to_buy, user):
    try:
        user_id = str(user.id)
        buyer, _ = get_player_data(message, user_id)
        
        lots = ah_data.get("lots", [])
        lot = next((l for l in lots if l["id"] == lot_id), None)
        
        if not lot:
            bot.send_message(message.chat.id, "❌ Ошибка: лот не найден.")
            return

        if str(lot["seller_id"]) == str(user_id):
            bot.send_message(message.chat.id, "❌ Вы не можете купить собственный лот!")
            return

        total_price = lot["price"] * amount_to_buy
        
        if buyer.get("money", 0) < total_price:
            bot.send_message(message.chat.id, f"❌ Недостаточно средств! Нужно {total_price} 💰", parse_mode="HTML")
            return

        # Процесс покупки
        buyer["money"] -= total_price
        
        # Находим продавца и отдаем ему деньги
        seller_id = lot["seller_id"]
        if seller_id in players_data:
            players_data[seller_id]["money"] = players_data[seller_id].get("money", 0) + total_price
            try:
                bot.send_message(
                    seller_id,
                    f"💰 У вас купили <b>{lot['item_name']}</b> (x{amount_to_buy}) за <b>{total_price}</b>!",
                    parse_mode="HTML"
                )
            except:
                pass

        # Добавляем цветок покупателю
        if "inventory" not in buyer: buyer["inventory"] = {}
        if "flowers" not in buyer["inventory"]: buyer["inventory"]["flowers"] = {}
        
        flower_name = lot["item_name"]
        buyer["inventory"]["flowers"][flower_name] = buyer["inventory"]["flowers"].get(flower_name, 0) + amount_to_buy
        
        # Обновляем или удаляем лот
        lot["amount"] -= amount_to_buy
        if lot["amount"] <= 0:
            ah_data["lots"].remove(lot)
        
        save_data()
        
        bot.send_message(
            message.chat.id,
            f"✅ Вы успешно купили <b>{flower_name}</b> (x{amount_to_buy}) за <b>{total_price}</b> 💰!",
            parse_mode="HTML"
        )
        
    except Exception as e:
        error_logger(user.username, "buy_final", e)
        bot.send_message(message.chat.id, "Произошла ошибка при завершении покупки🤯")
@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "❌ Операция отменена",
            parse_mode="HTML",
        )
    except Exception:
        pass




