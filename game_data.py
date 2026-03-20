# game_data.py
from config import RARITY_GROW_TIME_MINUTES, GROWING_PLANT_WATER_TIME_MINUTES

seeds_data = {
    "обычный": {
        "⚪️роза⚪️": {"price": 10, "income": 2, "grow_time": 5},
        "⚪️тюльпан⚪️": {"price": 8, "income": 1, "grow_time": 3},
        "⚪️нарцисс⚪️": {"price": 9, "income": 2, "grow_time": 4},
        "⚪️астра⚪️": {"price": 7, "income": 1, "grow_time": 3},
        "⚪️барвинок⚪️": {"price": 6, "income": 1, "grow_time": 3},
        "⚪️календула⚪️": {"price": 5, "income": 1, "grow_time": 2},
        "⚪️примула⚪️": {"price": 6, "income": 1, "grow_time": 2},
        "⚪️маргаритка⚪️": {"price": 5, "income": 1, "grow_time": 2},
        "⚪️незабудка⚪️": {"price": 6, "income": 1, "grow_time": 2},
        "⚪️виола⚪️": {"price": 7, "income": 2, "grow_time": 3},
        "⚪️петуния⚪️": {"price": 7, "income": 2, "grow_time": 3},
        "⚪️лобелия⚪️": {"price": 6, "income": 1, "grow_time": 2},
        "⚪️агератум⚪️": {"price": 5, "income": 1, "grow_time": 2},
        "⚪️космея⚪️": {"price": 6, "income": 1, "grow_time": 3}
    },

    "редкий": {
        "🔵лилия🔵": {"price": 25, "income": 5, "grow_time": 7},
        "🔵пион🔵": {"price": 30, "income": 6, "grow_time": 8},
        "🔵георгин🔵": {"price": 28, "income": 5, "grow_time": 7},
        "🔵гортензия🔵": {"price": 35, "income": 6, "grow_time": 8},
        "🔵флокс🔵": {"price": 22, "income": 4, "grow_time": 6},
        "🔵ирис🔵": {"price": 25, "income": 5, "grow_time": 7},
        "🔵лаванда🔵": {"price": 24, "income": 5, "grow_time": 6},
        "🔵гладиолус🔵": {"price": 30, "income": 6, "grow_time": 8},
        "🔵гвоздика🔵": {"price": 20, "income": 4, "grow_time": 6},
        "🔵настурция🔵": {"price": 18, "income": 3, "grow_time": 5},
        "🔵сальвия🔵": {"price": 20, "income": 4, "grow_time": 6},
        "🔵клематис🔵": {"price": 32, "income": 7, "grow_time": 8},
        "🔵вербена🔵": {"price": 21, "income": 4, "grow_time": 5}
    },

    "эпический": {
        "🟣орхидея🟣": {"price": 70, "income": 15, "grow_time": 12},
        "🟣азалия🟣": {"price": 65, "income": 14, "grow_time": 12},
        "🟣рододендрон🟣": {"price": 75, "income": 16, "grow_time": 13},
        "🟣эустома🟣": {"price": 80, "income": 18, "grow_time": 14},
        "🟣альстромерия🟣": {"price": 85, "income": 18, "grow_time": 15},
        "🟣амариллис🟣": {"price": 90, "income": 20, "grow_time": 15},
        "🟣глориоза🟣": {"price": 95, "income": 22, "grow_time": 16},
        "🟣диффенбахия🟣": {"price": 70, "income": 15, "grow_time": 12},
        "🟣калатея🟣": {"price": 68, "income": 14, "grow_time": 11},
        "🟣филодендрон🟣": {"price": 72, "income": 16, "grow_time": 13},
        "🟣стрелиция🟣": {"price": 100, "income": 25, "grow_time": 18},
        "🟣спатифиллум🟣": {"price": 85, "income": 18, "grow_time": 14},
        "🟣гербера🟣": {"price": 60, "income": 12, "grow_time": 10}
    },

    "легендарный": {
        "🟡магнолия🟡": {"price": 200, "income": 45, "grow_time": 25},
        "🟡сирень🟡": {"price": 180, "income": 40, "grow_time": 22},
        "🟡жасмин🟡": {"price": 190, "income": 42, "grow_time": 23},
        "🟡антуриум🟡": {"price": 210, "income": 50, "grow_time": 26},
        "🟡монстера🟡": {"price": 230, "income": 55, "grow_time": 28},
        "🟡замиокулькас🟡": {"price": 220, "income": 52, "grow_time": 27},
        "🟡филодендрон гигантский🟡": {"price": 250, "income": 60, "grow_time": 30},
        "🟡толстянка🟡": {"price": 200, "income": 45, "grow_time": 25},
        "🟡фикус🟡": {"price": 240, "income": 55, "grow_time": 29},
        "🟡стефанотис (легендарная лиана)🟡": {"price": 260, "income": 65, "grow_time": 32}
    }
}

flower_combinations = {
    "Весенняя нежность": {
        "flowers": ["⚪️роза⚪️", "⚪️тюльпан⚪️", "⚪️нарцисс⚪️"],
        "effect": "Ускорение роста",
        "effect_type": "speed_growth",
        "effect_value": 0.15,
        "description": "Все растения в саду растут на 15% быстрее"
    },
    "Летний букет": {
        "flowers": ["⚪️астра⚪️", "⚪️барвинок⚪️", "⚪️календула⚪️"],
        "effect": "Бонус к доходу",
        "effect_type": "bonus_income",
        "effect_value": 0.20,
        "description": "Доход от всех цветов увеличивается на 20%"
    },
    "Деревенский сад": {
        "flowers": ["⚪️примула⚪️", "⚪️маргаритка⚪️", "⚪️незабудка⚪️"],
        "effect": "Защита от высыхания",
        "effect_type": "water_time",
        "effect_value": 0.30,
        "description": "Время до высыхания увеличивается на 30% (30 минут → 39 минут)"
    },
    "Яркая палитра": {
        "flowers": ["⚪️виола⚪️", "⚪️герань⚪️", "⚪️петуния⚪️"],
        "effect": "Бонусные монеты",
        "effect_type": "bonus_money",
        "effect_value": 50,
        "description": "Ежедневный бонус +50 монет при входе в игру"
    },
    "Скромная красота": {
        "flowers": ["⚪️лобелия⚪️", "⚪️агератум⚪️", "⚪️космея⚪️"],
        "effect": "Экономия воды",
        "effect_type": "water_interval",
        "effect_value": 0.25,
        "description": "Интервал между поливами увеличивается на 25% (6 часов → 7.5 часов)"
    },
    "Королевская роскошь": {
        "flowers": ["🔵лилия🔵", "🔵пион🔵"],
        "effect": "Королевский доход",
        "effect_type": "bonus_income",
        "effect_value": 0.35,
        "description": "Доход от всех цветов увеличивается на 35%"
    },
    "Благородный дуэт": {
        "flowers": ["🔵георгин🔵", "🔵гортензия🔵"],
        "effect": "Благородное ускорение",
        "effect_type": "speed_growth",
        "effect_value": 0.25,
        "description": "Все растения в саду растут на 25% быстрее"
    },
    "Фиолетовая симфония": {
        "flowers": ["🔵флокс🔵", "🔵ирис🔵", "🔵лаванда🔵"],
        "effect": "Успокаивающий аромат",
        "effect_type": "water_time",
        "effect_value": 0.40,
        "description": "Время до высыхания увеличивается на 40% (30 минут → 42 минуты)"
    },
    "Величественный триумф": {
        "flowers": ["🔵гладиолус🔵", "🔵гвоздика🔵"],
        "effect": "Триумфальный бонус",
        "effect_type": "bonus_money",
        "effect_value": 100,
        "description": "Ежедневный бонус +100 монет при входе в игру"
    },
    "Ароматный сад": {
        "flowers": ["🔵настурция🔵", "🔵сальвия🔵", "🔵вербена🔵"],
        "effect": "Ароматная защита",
        "effect_type": "water_interval",
        "effect_value": 0.30,
        "description": "Интервал между поливами увеличивается на 30% (6 часов → 7.8 часов)"
    },
    "Винтажная элегантность": {
        "flowers": ["🔵клематис🔵", "⚪️роза⚪️"],
        "effect": "Элегантный рост",
        "effect_type": "speed_growth",
        "effect_value": 0.20,
        "description": "Все растения в саду растут на 20% быстрее"
    },
    "Экзотическая роскошь": {
        "flowers": ["🟣орхидея🟣", "🟣азалия🟣"],
        "effect": "Экзотический доход",
        "effect_type": "bonus_income",
        "effect_value": 0.50,
        "description": "Доход от всех цветов увеличивается на 50%"
    },
    "Тропический рай": {
        "flowers": ["🟣рододендрон🟣", "🟣эустома🟣", "🟣альстромерия🟣"],
        "effect": "Тропическое ускорение",
        "effect_type": "speed_growth",
        "effect_value": 0.35,
        "description": "Все растения в саду растут на 35% быстрее"
    },
    "Королевское великолепие": {
        "flowers": ["🟣амариллис🟣", "🟣глориоза🟣"],
        "effect": "Великолепный бонус",
        "effect_type": "bonus_money",
        "effect_value": 200,
        "description": "Ежедневный бонус +200 монет при входе в игру"
    },
    "Тропическая листва": {
        "flowers": ["🟣диффенбахия🟣", "🟣калатея🟣", "🟣филодендрон🟣"],
        "effect": "Влажная защита",
        "effect_type": "water_time",
        "effect_value": 0.50,
        "description": "Время до высыхания увеличивается на 50% (30 минут → 45 минут)"
    },
    "Райская птица": {
        "flowers": ["🟣стрелиция🟣", "🟣спатифиллум🟣"],
        "effect": "Райский доход",
        "effect_type": "bonus_income",
        "effect_value": 0.45,
        "description": "Доход от всех цветов увеличивается на 45%"
    },
    "Яркое солнце": {
        "flowers": ["🟣гербера🟣", "⚪️календула⚪️"],
        "effect": "Солнечная энергия",
        "effect_type": "speed_growth",
        "effect_value": 0.30,
        "description": "Все растения в саду растут на 30% быстрее"
    },
    "Легендарная красота": {
        "flowers": ["🟡магнолия🟡", "🟡сирень🟡"],
        "effect": "Легендарный доход",
        "effect_type": "bonus_income",
        "effect_value": 0.75,
        "description": "Доход от всех цветов увеличивается на 75%"
    },
    "Ароматное облако": {
        "flowers": ["🟡жасмин🟡", "🟡сирень🟡"],
        "effect": "Облако защиты",
        "effect_type": "water_interval",
        "effect_value": 0.50,
        "description": "Интервал между поливами увеличивается на 50% (6 часов → 9 часов)"
    },
    "Тропический гигант": {
        "flowers": ["🟡антуриум🟡", "🟡монстера🟡"],
        "effect": "Гигантское ускорение",
        "effect_type": "speed_growth",
        "effect_value": 0.40,
        "description": "Все растения в саду растут на 40% быстрее"
    },
    "Денежное дерево": {
        "flowers": ["🟡замиокулькас🟡", "🟡толстянка🟡"],
        "effect": "Денежный поток",
        "effect_type": "bonus_money",
        "effect_value": 500,
        "description": "Ежедневный бонус +500 монет при входе в игру"
    },
    "Великан сада": {
        "flowers": ["🟡филодендрон гигантский🟡", "🟡фикус🟡"],
        "effect": "Великанский доход",
        "effect_type": "bonus_income",
        "effect_value": 0.60,
        "description": "Доход от всех цветов увеличивается на 60%"
    },
    "Легендарная лиана": {
        "flowers": ["🟡стефанотис (легендарная лиана)🟡", "🔵клематис🔵"],
        "effect": "Лианная защита",
        "effect_type": "water_time",
        "effect_value": 0.60,
        "description": "Время до высыхания увеличивается на 60% (30 минут → 48 минут)"
    },
    "Смешанная классика": {
        "flowers": ["⚪️роза⚪️", "🔵лилия🔵"],
        "effect": "Классический баланс",
        "effect_type": "bonus_income",
        "effect_value": 0.25,
        "description": "Доход от всех цветов увеличивается на 25%"
    },
    "Роскошный микс": {
        "flowers": ["🔵пион🔵", "🟣орхидея🟣"],
        "effect": "Роскошный рост",
        "effect_type": "speed_growth",
        "effect_value": 0.30,
        "description": "Все растения в саду растут на 30% быстрее"
    },
    "Весенняя свежесть": {
        "flowers": ["⚪️тюльпан⚪️", "⚪️нарцисс⚪️", "🔵ирис🔵"],
        "effect": "Свежая энергия",
        "effect_type": "speed_growth",
        "effect_value": 0.18,
        "description": "Все растения в саду растут на 18% быстрее"
    },
    "Летний аромат": {
        "flowers": ["🔵лаванда🔵", "⚪️герань⚪️", "🟡жасмин🟡"],
        "effect": "Ароматная защита",
        "effect_type": "water_interval",
        "effect_value": 0.35,
        "description": "Интервал между поливами увеличивается на 35% (6 часов → 8.1 часов)"
    },
    "Осенняя палитра": {
        "flowers": ["🔵гортензия🔵", "⚪️астра⚪️", "🟣гербера🟣"],
        "effect": "Осенний урожай",
        "effect_type": "bonus_income",
        "effect_value": 0.30,
        "description": "Доход от всех цветов увеличивается на 30%"
    },
    "Зимняя элегантность": {
        "flowers": ["🟣орхидея🟣", "🟡магнолия🟡"],
        "effect": "Элегантная защита",
        "effect_type": "water_time",
        "effect_value": 0.45,
        "description": "Время до высыхания увеличивается на 45% (30 минут → 43.5 минуты)"
    },
    "Романтический букет": {
        "flowers": ["⚪️роза⚪️", "🔵пион🔵", "🟣эустома🟣"],
        "effect": "Романтический бонус",
        "effect_type": "bonus_money",
        "effect_value": 150,
        "description": "Ежедневный бонус +150 монет при входе в игру"
    },
    "Средиземноморский сад": {
        "flowers": ["🔵лаванда🔵", "⚪️герань⚪️", "🔵вербена🔵"],
        "effect": "Средиземноморская защита",
        "effect_type": "water_interval",
        "effect_value": 0.40,
        "description": "Интервал между поливами увеличивается на 40% (6 часов → 8.4 часов)"
    },
    "Азиатская экзотика": {
        "flowers": ["🟣орхидея🟣", "🟣азалия🟣", "🟡жасмин🟡"],
        "effect": "Экзотическое ускорение",
        "effect_type": "speed_growth",
        "effect_value": 0.45,
        "description": "Все растения в саду растут на 45% быстрее"
    },
    "Современный минимализм": {
        "flowers": ["🟣калатея🟣", "🟡монстера🟡", "🟡фикус🟡"],
        "effect": "Минималистичная защита",
        "effect_type": "water_time",
        "effect_value": 0.55,
        "description": "Время до высыхания увеличивается на 55% (30 минут → 46.5 минут)"
    }
}

seeds_price = {
    "обычный": 10,
    "редкий": 50,
    "эпический": 150,
    "легендарный": 500,
}

rarity_grow_time_minutes = RARITY_GROW_TIME_MINUTES

growing_plant_water_time_minutes = GROWING_PLANT_WATER_TIME_MINUTES

rarity_grow_chance = {
    "обычный": ["обычный"],
    "редкий": ["обычный", "редкий"],
    "эпический": ["эпический"] + ["редкий"] * 2 + ["обычный"],
    "легендарный": ["легендарный"] + ["эпический"] * 4 + ["обычный"] * 2,
}
