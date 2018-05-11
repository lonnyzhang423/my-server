import json
import os

__all__ = ["Config", ]


def _load_config():
    file = os.path.join(os.path.dirname(__file__), "config.json")
    with open(file, encoding="utf8") as f:
        return json.load(f)


Config = _load_config()
