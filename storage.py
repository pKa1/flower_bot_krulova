# storage.py
import json
import os
from config import DATA_FILE

AH_FILE = "ah_data.json"

players_data = {}
ah_data = {}


def save_data() -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(players_data, f, ensure_ascii=False, indent=2)
    
    with open(AH_FILE, "w", encoding="utf-8") as f:
        json.dump(ah_data, f, ensure_ascii=False, indent=2)


def load_data() -> None:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            players_data.clear()
            players_data.update(data)
    
    if os.path.exists(AH_FILE):
        with open(AH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            ah_data.clear()
            ah_data.update(data)
