import json


def json_2_dict(file_path: str):
    with open(file_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    return data