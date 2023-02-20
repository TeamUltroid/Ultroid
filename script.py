import json
import os

PATH = r"D:\PluginManagerAPI\data.json"
with open(PATH, "r") as file:
    Content = json.load(file)

folder = "inline"

files = os.listdir(folder)
for file in files:
    if file[:-3] not in Content:
        Content[file[:-3]] = {
            "path": f"{folder}/{file}",
            "repo": "TeamUltroid/Ultroid/@stale",
            "version": 0
        }

with open(PATH, "w") as file:
    json.dump(Content, file, indent=1)