import json
import os
from typing import Any

from dotenv import load_dotenv

from .i18n import PersonalityToneType

load_dotenv()


def load_global_config() -> dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "assets", "config.json")

    config: dict[str, Any] = {
        "bot_name": "TehBot",
        "default_language": "en",
        "bot_prefix": "pox/",
        "default_personality": PersonalityToneType.CASUAL.value,
    }

    try:
        with open(path, encoding="utf-8") as f:
            config.update(json.load(f))
    except FileNotFoundError:
        pass

    config["discord_token"] = os.getenv("DISCORD_TOKEN")
    return config


global_config = load_global_config()
