import json

class CompositionsJSONReader:
    
    def __init__(self):
        try:
            with open('code/db/compositions.json', 'r') as f:
                self.data = json.load(f)
                print(self.data)
        except FileNotFoundError:
            print("Файл не найден")
        except json.JSONDecodeError:
            print("Ошибка в формате JSON")


    def get_all_compositions_labels(self):
        return self.data.keys()
    
    def get_composition_info(self, key):
        return self.data[key]["Info"]
    
    def get_composition(self, key):
        return self.data[key]["Composition"]
    
    def add_composition(self, composition_name, composition, overwrite = False):
        """
    Обновляет данные в JSON-файле. Если файла нет — создаёт его.
    
    :param new_data: Новые данные (словарь)
    :param filename: Путь к JSON-файлу
    :param overwrite: Если True, перезаписывает весь файл. Если False — объединяет данные.
    """
        new_data = {composition_name: {
             "Info": {},
             "Composition": composition
        }}
        with open('code/db/compositions.json', 'r') as f:
            self.data = json.load(f)
        try:
        # Читаем существующие данные, если файл есть
            if overwrite:
                        updated_data = new_data
            else:
                updated_data = {**self.data, **new_data}  # Объединяем словари
                    
                    # Записываем обратно
            with open('code/db/compositions.json', 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=4, ensure_ascii=False)
                    
                print(f"✅ Данные успешно обновлены в 'code/db/compositions.json'")
                return True
                
        except json.JSONDecodeError:
                    print("❌ Ошибка: Файл повреждён или не в JSON-формате!")
        except Exception as e:
                    print(f"❌ Ошибка: {e}")
        return False




if __name__ == '__main__':
    comp_db_reader = CompositionsJSONReader()
    print(comp_db_reader.get_all_compositions_labels())
    print(comp_db_reader.get_composition_info('Comp2'))
    print(comp_db_reader.get_composition('Comp1'))