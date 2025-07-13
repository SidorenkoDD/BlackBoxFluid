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
        with open('code/db/compositions.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    
    def get_composition_info(self, key):
        with open('code/db/compositions.json', 'r') as f:
            self.data = json.load(f)
        return self.data[key]["Info"]
    
    def get_composition(self, key):
        with open('code/db/compositions.json', 'r') as f:
                self.data = json.load(f)
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
                    
                print(f"Данные успешно обновлены в 'code/db/compositions.json'")
                return True
                
        except json.JSONDecodeError:
                    print("Ошибка: Файл повреждён или не в JSON-формате!")
        except Exception as e:
                    print(f"Ошибка: {e}")
        return False
    

    def update_composition(self, old_name, new_name, new_composition, new_info):
    # Загружаем текущие данные
        with open('code/db/compositions.json', 'r') as file:
            data = json.load(file)
        
        # Удаляем старую запись (если имя изменилось)
        if old_name in data.keys() and old_name != new_name:
            del data[old_name]
        
        # Добавляем/обновляем запись
        data[new_name] = {
            'Composition': new_composition,
            'Info': new_info
        }
        
        # Сохраняем обратно в файл
        with open('code/db/compositions.json', 'w') as file:
            json.dump(data, file, indent=4)

    def del_composition(self, key_to_remove):
        try:
            # Читаем данные из файла
            with open('code/db/compositions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Удаляем ключ
            if isinstance(key_to_remove, str):
                if key_to_remove in data:
                    del data[key_to_remove]
                else:
                    print(f"⚠️ Ключ '{key_to_remove}' не найден в файле")
                    return False
            elif isinstance(key_to_remove, list):
                # Для вложенных ключей (например, ['user', 'address', 'city'])
                current_level = data
                for key in key_to_remove[:-1]:
                    if key in current_level:
                        current_level = current_level[key]
                    else:
                        print(f"⚠️ Ключ '{key}' не найден в пути")
                        return False
                if key_to_remove[-1] in current_level:
                    del current_level[key_to_remove[-1]]
                else:
                    print(f"⚠️ Ключ '{key_to_remove[-1]}' не найден в пути")
                    return False

            # Записываем обновленные данные обратно
            with open('code/db/compositions.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(f"✅ Ключ '{key_to_remove}' успешно удалён из 'code/db/compositions.json'")
            return True

        except json.JSONDecodeError:
            print("❌ Ошибка: Файл повреждён или не в JSON-формате!")
        except Exception as e:
            print(f"❌ Произошла ошибка: {str(e)}")
        return False




if __name__ == '__main__':
    comp_db_reader = CompositionsJSONReader()
    print(comp_db_reader.get_all_compositions_labels())
    print(comp_db_reader.get_composition_info('Comp2'))
    print(comp_db_reader.get_composition('Comp1'))