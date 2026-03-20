# main.py
from storage import load_data, players_data
from quests import get_daily_quest
from services import start_growth_watcher
from bot_instance import bot
import handlers  # важно: импорт, чтобы зарегистрировать все хэндлеры


def main():
    global players_data
    try: load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        print("File not found. Creating a new one.")
    for uid in list(players_data.keys()):
        try:
            get_daily_quest(uid)
        except Exception as e:
            print(f"quest init error for {uid}: {e}")
    start_growth_watcher()
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
