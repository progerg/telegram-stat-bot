import json

with open('json/message.json', mode='r', encoding='utf-8') as json_file:
    MESSAGES = json.load(json_file)
