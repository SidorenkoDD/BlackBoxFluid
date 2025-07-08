import dearpygui.dearpygui as dpg
from gui.composition_window import CompositionWindow
from gui.flash_input_window import FlashInputWindow
from gui.library_window import LibraryWindow
from models.flash import FlashCalculator
from config import WINDOW_POSITIONS, COMPONENTS

class MainWindow:
    def __init__(self, calculator: FlashCalculator):
        self.calculator = calculator
        self.tag = "primary_window"
        
        # Создаем дочерние окна
        self.composition_window = CompositionWindow(
            calculator=calculator,
            position=WINDOW_POSITIONS["composition_window"],
            components=COMPONENTS
        )
        
        self.flash_input_window = FlashInputWindow(
            calculator=calculator,
            position=WINDOW_POSITIONS["flash_input_window"],
            calculate_callback=self.show_results
        )
        
        self.library_window = LibraryWindow(
            position=WINDOW_POSITIONS.get("library_window", {"x": 100, "y": 100})
        )

    def create(self):
        """Создаёт главное окно и меню приложения."""
        with dpg.window(label="Main Window", tag=self.tag):
            self._setup_main_menu()
    
    def _setup_main_menu(self):
        """Настраивает главное меню приложения."""
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                with dpg.menu(label='New'):
                    with dpg.menu(label='PVT'):
                        dpg.add_menu_item(label='BO', enabled=False)
                        dpg.add_menu_item(
                            label='Compositional',
                            callback=self.show_compositional_interface
                        )
                dpg.add_menu_item(label="Open", enabled=False)
                dpg.add_menu_item(label="Save", enabled=False)
                dpg.add_separator()
                dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

            with dpg.menu(label="Extensions"):
                dpg.add_menu_item(label="Import extension", enabled=False)
            
            with dpg.menu(label="Library"):
                dpg.add_menu_item(label="Open DB", callback=self.library_window.show)
            
            with dpg.menu(label="Info"):
                dpg.add_menu_item(label="About", enabled=False)

    def show_compositional_interface(self):
        """Показывает интерфейс для композиционного анализа."""
        self.composition_window.create()
        self.flash_input_window.create()

    def show_results(self):
        """Отображает результаты расчёта."""
        results = self.calculator.calculate_flash()
        ResultsWindow.show(
            results=str(results),
            position=WINDOW_POSITIONS["results_window"]
        )