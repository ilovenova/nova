import json
import os


def load_json(filename, default):
    if not os.path.exists(filename):
        save_json(filename, default)
        return default

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)