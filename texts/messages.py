import json

with open('json/messages.json', mode='r', encoding='utf-8') as json_file:
    MESSAGES = json.load(json_file)
