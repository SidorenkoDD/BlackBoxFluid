import dearpygui.dearpygui as dpg
from code.gui_v2.config import WINDOW_POSITIONS, COMPONENTS
from models.flash import FlashCalculator
from gui.main_window import MainWindow

def initialize_application() -> None:
    """Инициализирует и запускает приложение."""
    # Инициализация контекста Dear PyGui
    dpg.create_context()
    dpg.create_viewport(title="PVT Flash Calculator", width=850, height=700)
    
    # Создаём модель калькулятора
    calculator = FlashCalculator(components=COMPONENTS)
    
    # Создаём главное окно
    main_window = MainWindow(calculator=calculator, window_positions=WINDOW_POSITIONS)
    main_window.create()
    
    # Запуск приложения
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(main_window.tag, True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    initialize_application()