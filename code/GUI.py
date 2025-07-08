import dearpygui.dearpygui as dpg
from typing import Dict, List
from DBReader import DBReader
import json
import yaml
from pathlib import Path

# Константы
WINDOW_POSITIONS = {
    "composition_window": {"x": 10, "y": 30, "width": 400, "height": 300},
    "flash_input_window": {"x": 420, "y": 30, "width": 400, "height": 300},
    "results_window": {"x": 420, "y": 340, "width": 400, "height": 300}
}

COMPONENTS = ['C1', 'C2', 'C3', 'nC4', 'iC4', 'nC5', 'iC5']

class FlashCalculator:
    def __init__(self):
        self.pressure = 0.0
        self.temperature = 0.0
        self.composition = {comp: 0.0 for comp in COMPONENTS}

    def update_composition(self, component: str, value: float):
        if component in self.composition:
            self.composition[component] = value

    def update_pt(self, pressure: float, temperature: float):
        self.pressure = pressure
        self.temperature = temperature

    def calculate_flash(self) -> str:
        # Здесь должна быть реальная логика расчёта
        # Пока просто возвращаем собранные данные
        comp_str = "\n".join([f"{comp}: {val:.3f}" for comp, val in self.composition.items()])
        return (
            f"Flash calculation results:\n\n"
            f"Pressure: {self.pressure:.2f} bar\n"
            f"Temperature: {self.temperature:.2f} °C\n\n"
            f"Composition:\n{comp_str}"
        )

flash_calc = FlashCalculator()

def menu_callback(sender, app_data, user_data):
    print(f"Selected menu item: {user_data}")

def create_composition_table() -> None:
    """Создаёт таблицу для ввода состава."""
    pos = WINDOW_POSITIONS["composition_window"]
    
    if dpg.does_item_exist('composition_window'):
        dpg.delete_item('composition_window')

    with dpg.window(
        label='Composition Input',
        tag='composition_window',
        width=pos['width'],
        height=pos['height'],
        pos=(pos['x'], pos['y']),
        no_resize=False,
        no_collapse=False,
        no_close=True
    ):
        with dpg.table(header_row=True):
            dpg.add_table_column(label='Component')
            dpg.add_table_column(label='Mole Fraction')
            
            for component in COMPONENTS:
                with dpg.table_row():
                    dpg.add_text(component)
                    dpg.add_input_float(
                        default_value=0.0,
                        tag=f"input_{component}",
                        step=0.05,
                        callback=lambda s, a, u: flash_calc.update_composition(u, a),
                        user_data=component
                    )

def create_flash_input_window() -> None:
    """Создаёт окно для ввода параметров P и T."""
    pos = WINDOW_POSITIONS['flash_input_window']

    if dpg.does_item_exist('flash_input_window'):
        dpg.delete_item('flash_input_window')
        
    with dpg.window(
        label='Flash Input Parameters',
        tag='flash_input_window',
        width=pos['width'],
        height=pos['height'],
        pos=(pos['x'], pos['y']),
        no_resize=False,
        no_collapse=False,
        no_close=True
    ):
        dpg.add_input_float(
            label='Pressure, bar',
            tag='input_pressure',
            callback=lambda s, a: flash_calc.update_pt(a, flash_calc.temperature)
        )
        dpg.add_input_float(
            label='Temperature, °C',
            tag='input_temperature',
            callback=lambda s, a: flash_calc.update_pt(flash_calc.pressure, a)
        )
        dpg.add_button(
            label='Calculate Flash',
            callback=show_flash_results
        )

def show_flash_results() -> None:
    """Отображает результаты расчёта."""
    pos = WINDOW_POSITIONS['results_window']
    
    if dpg.does_item_exist('results_window'):
        dpg.delete_item('results_window')

    with dpg.window(
        label='Flash Calculation Results',
        tag='results_window',
        width=pos['width'],
        height=pos['height'],
        pos=(pos['x'], pos['y']),
        no_resize=False,
        no_collapse=False,
        no_close=True
    ):
        results = flash_calc.calculate_flash()
        dpg.add_input_text(
            multiline=True,
            height=280,
            width=380,
            default_value=results,
            readonly=True,
            tag='flash_results_output'
        )

def show_compositional_interface() -> None:

    """Показывает интерфейс для композиционного анализа."""
    create_composition_table()
    create_flash_input_window()

def add_new_db():
    string_to_db = str(dpg.get_value('new_db_part'))

    fixed_yaml_data = string_to_db.replace("\t", "  ")
    new_data_dict = yaml.safe_load(fixed_yaml_data)

    yaml_file = Path("code/db.yaml")

    # Читаем существующие данные, если файл существует
    existing_data = {}
    if yaml_file.exists():
        with yaml_file.open('r') as f:
            existing_data = yaml.safe_load(f) or {}

    # Объединяем данные (существующие + новые)
    merged_data = {**existing_data, **new_data_dict}

    # Записываем объединённые данные обратно в файл
    with yaml_file.open('w') as f:
        yaml.dump(merged_data, f, sort_keys=False)



def show_add_to_db_window() -> None:
    if dpg.does_item_exist("add_to_db_window"):
        dpg.delete_item("add_to_db_window")

    with dpg.window(
        label= 'Add to db',
        tag= 'Add_to_db',        
        width=800,
        height=600,
        modal=True,
        no_close=False

    ):
        dpg.add_text('EXAMPLE\n DB Name\n--->"Component": value\n--->...')

        dpg.add_input_text(tag = 'new_db_part',height=250,multiline=True, tab_input=True)

        dpg.add_button(label='Submit', callback= add_new_db)



def show_library_window() -> None:
    """Показывает окно библиотеки с таблицей данных."""
    if dpg.does_item_exist("popup_window"):
        dpg.delete_item("popup_window")

    db = DBReader()
    library_keys = list(db.get_keys())  # Получаем список доступных ключей

    with dpg.window(
        tag="popup_window",
        label="DB Data",
        width=800,
        height=600,
        modal=False,
        no_close=False
    ):
        with dpg.group(horizontal=True):
            # Группа для списка библиотек
            with dpg.group(width=200):
                dpg.add_text("Select db item:")
                dpg.add_listbox(
                    tag='listbox_library',
                    items=library_keys,
                    num_items=min(15, len(library_keys)),
                    width=180,
                    callback=update_library_table
                )
                dpg.add_spacer(height=20)
                
                dpg.add_button(label= 'Add', callback= show_add_to_db_window)

                dpg.add_button(
                    label="Close",
                    callback=lambda: dpg.delete_item("popup_window")
                )

            # Группа для таблицы (справа от списка)
            with dpg.group(tag="library_table_group"):
                # Показываем первую таблицу по умолчанию, если есть данные
                if library_keys:
                    # Получаем данные для первого ключа
                    first_data = db.get_data(library_keys[0])
                    show_selected_library_table(first_data)

def show_selected_library_table(data: dict):
    """Отображает таблицу ключ-значение для полученных данных."""
    # Удаляем старую таблицу, если есть
    if dpg.does_item_exist("library_table"):
        dpg.delete_item("library_table")

    # Создаем новую таблицу
    with dpg.table(
        tag="library_table",
        parent="library_table_group",
        header_row=True,
        borders_innerH=True,
        borders_outerH=True,
        borders_innerV=True,
        borders_outerV=True,
        width=550,
        height=500
    ):
        if not data:
            dpg.add_text("No data available")
            return

        # Создаем колонки
        dpg.add_table_column(label="Component")
        dpg.add_table_column(label="Value")

        # Заполняем таблицу данными
        for key, value in data.items():
            with dpg.table_row():
                dpg.add_text(str(key))
                if isinstance(value, (dict, list)):
                    # Для сложных структур используем json форматирование
                    dpg.add_text(json.dumps(value, indent=2, ensure_ascii=False))
                else:
                    dpg.add_text(str(value))

def update_library_table(sender, app_data):
    """Обновляет таблицу при изменении выбора в списке."""
    selected_key = dpg.get_value(sender)
    db = DBReader()
    selected_data = db.get_data(selected_key)  # Получаем данные по выбранному ключу
    show_selected_library_table(selected_data)

def setup_main_menu() -> None:
    """Настраивает главное меню приложения."""
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            with dpg.menu(label='New'):
                with dpg.menu(label='PVT'):
                    dpg.add_menu_item(label='BO', enabled=False)
                    dpg.add_menu_item(
                        label='Compositional',
                        callback=show_compositional_interface
                    )
            dpg.add_menu_item(label="Open", callback=menu_callback, user_data="Open", enabled=False)
            dpg.add_menu_item(label="Save", callback=menu_callback, user_data="Save", enabled=False)
            dpg.add_separator()
            dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

        with dpg.menu(label="Extensions"):
            dpg.add_menu_item(label="Import extension", enabled=False)
        
        with dpg.menu(label="Library"):
            dpg.add_menu_item(label="Open DB", callback=show_library_window)

        with dpg.menu(label="Info"):
            dpg.add_menu_item(label="About", enabled=False)

def initialize_application() -> None:
    """Инициализирует и запускает приложение."""
    dpg.create_context()
    dpg.create_viewport(title="PVT Flash Calculator", width=850, height=700)
    
    with dpg.window(label="Main Window", tag="primary_window"):
        setup_main_menu()
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    initialize_application()