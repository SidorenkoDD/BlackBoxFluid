import json

class ModelJSONReader:

    def __init__(self):
        try:
            with open('code/db/compositions.json', 'r') as f:
                self.data = json.load(f)
                print(self.data)

        except FileNotFoundError:
            print("Файл не найден")
        except json.JSONDecodeError:
            print("Ошибка в формате JSON")


    def get_all_models_labels(self):
        ...