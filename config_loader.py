import json
from pathlib import Path


CONFIG_PATH = Path(__file__).parent / "config" / "settings.json"


def load_config():

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    return config