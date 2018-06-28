import json
import os

__all__ = ["Config", ]


def _load_config():
    file = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(file, encoding="utf8") as f:
            return json.load(f)
    except IOError:
        return {}


Config = _load_config()
