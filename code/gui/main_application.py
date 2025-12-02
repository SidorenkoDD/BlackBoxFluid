# main_application.py
import dearpygui.dearpygui as dpg
from fluid_database import FluidDatabase
from component_manager import ComponentManager
from composition_editor import CompositionEditor
from fluid_properties_editor import FluidPropertiesEditor
from bips_editor import BIPSEditor
from fluid_creator import FluidCreator
from theme_manager import ThemeManager

class PVTCompositionManager:
    """Главный класс приложения PVT Simulator"""
    
    def __init__(self):
        print("Initializing PVTCompositionManager...")
        
        # Инициализация компонентов в правильном порядке
        self.fluid_db = FluidDatabase()
        self.component_manager = ComponentManager()
        
        # Создаем редакторы
        self.composition_editor = CompositionEditor(self.component_manager)
        self.properties_editor = FluidPropertiesEditor()
        self.bips_editor = BIPSEditor()
        
        # Связываем редактор состава с обновлением UI
        self.composition_editor.on_composition_change = self.on_composition_change
        
        # Создаем окно создания флюида
        self.fluid_creator = FluidCreator(
            component_manager=self.component_manager,
            composition_editor=self.composition_editor,
            properties_editor=self.properties_editor,
            bips_editor=self.bips_editor,
            save_callback=self.save_new_fluid
        )
        
        # Настройка GUI должна быть последней
        self.setup_gui()
    
    def setup_gui(self):
        """Настройка графического интерфейса"""
        print("Setting up GUI...")
        
        # Создаем контекст Dear PyGui
        dpg.create_context()
        
        # Создаем viewport
        dpg.create_viewport(
            title='PVT Simulator', 
            width=1400, 
            height=900,
            min_width=1000,
            min_height=700
        )
        
        # Настраиваем тему
        ThemeManager.setup_global_theme()
        
        # Создаем главное окно
        with dpg.window(tag="Primary Window", no_scrollbar=True):
            self.setup_main_interface()
        
        # Завершаем настройку
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)
        dpg.maximize_viewport()
        
        print("GUI setup completed successfully")
    
    def setup_main_interface(self):
        """Настройка основного интерфейса"""
        with dpg.group(horizontal=True):
            # Боковая панель
            with dpg.child_window(width=350, tag="fluids_sidebar"):
                self.setup_fluids_sidebar()
            
            # Основная область
            with dpg.child_window(tag="main_content_area"):
                self.setup_main_content()
    
    def setup_fluids_sidebar(self):
        """Настройка боковой панели флюидов"""
        dpg.add_text("Fluids Database", color=(0, 200, 255))
        
        # Поиск
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="fluid_search", hint="Search fluids...", width=250)
            dpg.add_button(label="Search", callback=self.search_fluids)
        
        dpg.add_separator()
        dpg.add_text("Available Fluids:")
        
        # Контейнер для списка флюидов
        with dpg.child_window(height=400, tag="fluids_accordion_container"):
            self.refresh_fluids_list()
        
        dpg.add_separator()
        dpg.add_button(
            label="+ New Fluid", 
            callback=self.show_new_fluid_window, 
            width=330, 
            height=30
        )
    
    def setup_main_content(self):
        """Настройка основной области контента"""
        dpg.add_text("PVT Simulator", color=(0, 200, 255))
        dpg.add_text(
            "Select a fluid from the sidebar to start working", 
            color=(150, 150, 150), 
            tag="main_content_message"
        )
        
        # Информация о выбранном флюиде (изначально скрыта)
        with dpg.group(tag="fluid_info_group", show=False):
            dpg.add_separator()
            dpg.add_text("Selected Fluid Information", color=(0, 200, 255))
            
            with dpg.table(tag="fluid_info_table", header_row=True, 
                          borders_innerH=True, borders_outerH=True):
                dpg.add_table_column(label="Property")
                dpg.add_table_column(label="Value")
                
                # Свойства флюида
                properties = [
                    ("Name", "info_name"),
                    ("Type", "info_type"),
                    ("Components Count", "info_components"),
                    ("Molecular Weight", "info_mw"),
                    ("Date Created", "info_date")
                ]
                
                for prop_name, tag in properties:
                    with dpg.table_row():
                        dpg.add_text(prop_name)
                        dpg.add_text("", tag=tag)
            
            dpg.add_separator()
        
        # Вкладки расчетов (изначально скрыты)
        with dpg.group(tag="calculation_tabs", show=False):
            with dpg.tab_bar():
                with dpg.tab(label="Properties"):
                    dpg.add_text("Fluid properties will be displayed here")
                with dpg.tab(label="Composition"):
                    dpg.add_text("Detailed composition analysis will be displayed here")
                with dpg.tab(label="Calculations"):
                    dpg.add_text("Calculation results will be displayed here")
    
    def refresh_fluids_list(self):
        """Обновление списка флюидов"""
        # Очищаем контейнер
        if dpg.does_item_exist("fluids_accordion_container"):
            # Удаляем всех детей контейнера
            children = dpg.get_item_children("fluids_accordion_container", 1)
            for child in children:
                dpg.delete_item(child)
        
        # Если флюидов нет, показываем сообщение
        if not self.fluid_db.fluids:
            dpg.add_text("No fluids available", tag="no_fluids_text", parent="fluids_accordion_container")
            return
        
        # Добавляем флюиды в аккордеон
        for i, fluid in enumerate(self.fluid_db.fluids):
            with dpg.collapsing_header(
                label=fluid["name"], 
                tag=f"fluid_header_{i}",
                parent="fluids_accordion_container",
                default_open=False,
                closable=False
            ):
                with dpg.group():
                    dpg.add_text(f"Type: {fluid['type']}", color=(200, 200, 0))
                    dpg.add_text(f"Components: {fluid['components']}")
                    dpg.add_text(f"Molecular Weight: {fluid['mw']}")
                    dpg.add_text(f"Date: {fluid['date']}")
                    
                    # Кнопки действий
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Select", 
                            callback=lambda s, d, idx=i: self.on_fluid_selected(idx),
                            width=80
                        )
                        dpg.add_button(
                            label="Copy", 
                            callback=lambda s, d, idx=i: self.copy_fluid(idx),
                            width=60
                        )
                        dpg.add_button(
                            label="Delete", 
                            callback=lambda s, d, idx=i: self.delete_fluid(idx),
                            width=60
                        )
    
    def on_composition_change(self):
        """Обработчик изменения состава"""
        self.fluid_creator.update_composition_summary()
    
    def show_new_fluid_window(self):
        """Показать окно создания флюида"""
        self.fluid_creator.show_window()
    
    def save_new_fluid(self):
        """Сохранение нового флюида"""
        try:
            fluid_data = self.fluid_creator.get_fluid_data()
            self.fluid_db.add_fluid(fluid_data)
            self.refresh_fluids_list()
            self.fluid_creator.hide_window()
            print("New fluid saved successfully")
        except Exception as e:
            print(f"Error saving fluid: {e}")
    
    def on_fluid_selected(self, index):
        """Обработчик выбора флюида"""
        fluid = self.fluid_db.get_fluid_by_index(index)
        if fluid:
            self.fluid_db.current_fluid = fluid
            
            # Обновляем информацию о флюиде
            dpg.set_value("info_name", fluid["name"])
            dpg.set_value("info_type", fluid["type"])
            dpg.set_value("info_components", str(fluid["components"]))
            dpg.set_value("info_mw", str(fluid["mw"]))
            dpg.set_value("info_date", fluid["date"])
            
            # Показываем информацию и вкладки
            dpg.hide_item("main_content_message")
            dpg.show_item("fluid_info_group")
            dpg.show_item("calculation_tabs")
    
    def copy_fluid(self, index):
        """Копирование флюида"""
        copied_fluid = self.fluid_db.copy_fluid(index)
        if copied_fluid:
            self.fluid_db.add_fluid(copied_fluid)
            self.refresh_fluids_list()
    
    def delete_fluid(self, index):
        """Удаление флюида"""
        # Временная заглушка - можно реализовать позже
        print(f"Delete fluid at index {index}")
        # self.fluid_db.delete_fluid(index)
        # self.refresh_fluids_list()
    
    def search_fluids(self):
        """Поиск флюидов"""
        search_term = dpg.get_value("fluid_search")
        print(f"Searching for: {search_term}")
        # Базовая реализация поиска
        # TODO: Реализовать полноценный поиск
    
    def run(self):
        """Запуск приложения"""
        print("Starting Dear PyGui main loop...")
        dpg.start_dearpygui()
        dpg.destroy_context()
        print("Application closed")

        
# Точка входа
if __name__ == "__main__":
    app = PVTCompositionManager()
    app.run()