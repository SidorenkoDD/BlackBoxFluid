import dearpygui.dearpygui as dpg
from typing import Dict, List

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
            dpg.add_menu_item(label="Open library", enabled=False)

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