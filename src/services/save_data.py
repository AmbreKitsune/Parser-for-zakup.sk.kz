from core.paths import SAVE_ID_FILE

def get_data_old_id():
    if SAVE_ID_FILE.exists():
        with open(SAVE_ID_FILE, "r", encoding="utf-8") as file:
            url_id = file.readline()

        return url_id.split(",")
    return []

def save_data_old_id(list_items):
    with open(SAVE_ID_FILE, "w", encoding='UTF-8') as file:
        file.write(",".join(list_items))

