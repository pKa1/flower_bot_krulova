import os
TOKEN = "7641282201:AAExic7nHEVuh13lpoRZIz3F8QCDRKYCfU0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "players_data.json")
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

# Время роста в минутах для каждой редкости
RARITY_GROW_TIME_MINUTES = {
    "обычный": 10,
    "редкий": 30,
    "эпический": 60,
    "легендарный": 120,
}

# Время до высыхания растущего растения (в минутах)
GROWING_PLANT_WATER_TIME_MINUTES = 60
