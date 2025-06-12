import json, os
from typing import Optional


class TempConfigHandler:
    path = ".config/ultroid.json"

    def set(self, key: str, value: str):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        except FileNotFoundError:
            data = {}

        with open(self.path, "w") as f:
            data[key] = value
            json.dump(data, f, indent=4)

    def get(self, key: str) -> Optional[str]:
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
                return data.get(key)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def remove(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


temp_config_store = TempConfigHandler()
