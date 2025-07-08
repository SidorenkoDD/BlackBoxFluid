import dearpygui.dearpygui as dpg
import yaml
from pathlib import Path
from db.db_reader import DBReader

class AddDBWindow:
    def __init__(self):
        self.tag = "add_db_window"
        self.input_tag = "new_db_input"
    
    def show(self):
        """Показывает окно добавления в БД."""
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)

        with dpg.window(
            label='Add to Database',
            tag=self.tag,
            width=800,
            height=600,
            modal=True,
            no_close=False
        ):
            dpg.add_text('EXAMPLE FORMAT:\nDB_Name:\n  "Component1": value1\n  "Component2": value2\n  ...')
            dpg.add_input_text(
                tag=self.input_tag,
                height=250,
                multiline=True,
                tab_input=True
            )
            dpg.add_button(label='Submit', callback=self._add_to_db)

    def _add_to_db(self):
        """Добавляет новые данные в БД."""
        input_data = dpg.get_value(self.input_tag)
        if not input_data:
            return

        try:
            # Попытка загрузить YAML
            data = yaml.safe_load(input_data)
            if not data or not isinstance(data, dict):
                raise ValueError("Invalid YAML format")
            
            # Получаем путь к БД из DBReader
            db_reader = DBReader()
            db_path = Path(db_reader.db_path)
            
            # Читаем существующие данные
            existing_data = {}
            if db_path.exists():
                with db_path.open('r') as f:
                    existing_data = yaml.safe_load(f) or {}
            
            # Объединяем данные
            merged_data = {**existing_data, **data}
            
            # Записываем обратно
            with db_path.open('w') as f:
                yaml.dump(merged_data, f, sort_keys=False)
                
            # Закрываем окно
            dpg.delete_item(self.tag)
            
        except Exception as e:
            dpg.add_text(f"Error: {str(e)}", parent=self.tag, color=(255, 0, 0))