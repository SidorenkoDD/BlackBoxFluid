# fluid_creator.py
import dearpygui.dearpygui as dpg
from typing import Optional, Callable

class FluidCreator:
    """Окно создания и редактирования флюида"""
    
    def __init__(self, 
                 component_manager,
                 composition_editor,
                 properties_editor, 
                 bips_editor,
                 save_callback: Optional[Callable] = None):
        
        self.component_manager = component_manager
        self.composition_editor = composition_editor
        self.properties_editor = properties_editor
        self.bips_editor = bips_editor
        self.save_callback = save_callback
        
        self.current_tab = "composition"
        self.is_composition_normalized = False
        
        self.setup_window()
    
    def setup_window(self):
        """Настройка окна создания флюида"""
        with dpg.window(
            label="Create New Fluid", 
            tag="new_fluid_window", 
            width=1000, 
            height=700, 
            show=False, 
            modal=True,
            on_close=self.hide_window
        ):
            with dpg.group(horizontal=True, height=-1):
                # Левая панель - основная информация
                with dpg.child_window(width=300):
                    self._setup_main_info_panel()
                
                # Правая панель - вкладки
                with dpg.child_window():
                    self._setup_tab_system()
    
    def _setup_tab_system(self):
        """Система вкладок"""
        # Кнопки переключения вкладок
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Composition Editor",
                tag="tab_composition",
                callback=lambda: self.switch_tab("composition"),
                width=150
            )
            dpg.add_button(
                label="Properties & Correlations", 
                tag="tab_properties",
                callback=lambda: self.switch_tab("properties"),
                width=180,
                enabled=False
            )
            dpg.add_button(
                label="BIPS",
                tag="tab_bips", 
                callback=lambda: self.switch_tab("bips"),
                width=100,
                enabled=False
            )
        
        # Контейнеры для содержимого вкладок
        with dpg.group(width=-1, height=-1):
            # Вкладка Composition Editor
            with dpg.child_window(tag="tab_content_composition", show=True, width=-1, height=-1):
                self.composition_editor.setup_editor("tab_content_composition")
            
            # Вкладка Properties & Correlations
            with dpg.child_window(tag="tab_content_properties", show=False, width=-1, height=-1):
                self.properties_editor.setup_editor("tab_content_properties")
            
            # Вкладка BIPS
            with dpg.child_window(tag="tab_content_bips", show=False, width=-1, height=-1):
                self.bips_editor.setup_editor("tab_content_bips")
    
    def _setup_main_info_panel(self):
        """Панель основной информации"""
        dpg.add_text("Main Information", color=(0, 200, 255))
        
        with dpg.table(header_row=False, borders_innerH=True):
            dpg.add_table_column(width_fixed=True, width=100)
            dpg.add_table_column(width_stretch=True)
            
            with dpg.table_row():
                dpg.add_text("Name")
                dpg.add_input_text(tag="new_fluid_name", default_value="New_Fluid", width=180)
            
            with dpg.table_row():
                dpg.add_text("Description")
                dpg.add_input_text(tag="new_fluid_desc", default_value="", width=180)
            
            with dpg.table_row():
                dpg.add_text("Source")
                dpg.add_input_text(tag="new_fluid_source", hint="Laboratory/Field", width=180)
        
        dpg.add_separator()
        self._setup_composition_tools()
        dpg.add_separator()
        self._setup_composition_summary()
        dpg.add_separator()
        self._setup_action_buttons()
    
    def _setup_composition_tools(self):
        """Инструменты для работы с составом"""
        dpg.add_text("Composition Tools", color=(200, 200, 0))
        
        tools = [
            ("Auto-Fill Fractions", self.composition_editor.auto_fill_fractions),
            ("Auto-Normalize", self.composition_editor.auto_normalize),
            ("Check Validity", self.composition_editor.check_validity),
            ("Clear All Components", self.composition_editor.clear_selected_components)
        ]
        
        for label, callback in tools:
            dpg.add_button(label=label, callback=callback, width=280)
    
    def _setup_composition_summary(self):
        """Сводная информация о составе"""
        dpg.add_text("Composition Summary", color=(200, 200, 0))
        
        with dpg.group():
            dpg.add_text("Total Components: 0", tag="total_components")
            dpg.add_text("Total Mole Fraction: 0.0000", tag="total_fraction")
            dpg.add_text("Normalized: No", tag="normalized_status")
            dpg.add_text("Additional Tabs: Locked", tag="tabs_status")
    
    def _setup_action_buttons(self):
        """Кнопки действий"""
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Save Fluid", 
                callback=self.save_fluid, 
                width=135
            )
            dpg.add_button(
                label="Cancel", 
                callback=self.hide_window, 
                width=135
            )
    
    def switch_tab(self, tab_name):
        """Переключение между вкладками"""
        # Скрываем все вкладки
        for tab in ["composition", "properties", "bips"]:
            content_tag = f"tab_content_{tab}"
            if dpg.does_item_exist(content_tag):
                dpg.hide_item(content_tag)
        
        # Показываем выбранную вкладку
        if tab_name == "composition":
            if dpg.does_item_exist("tab_content_composition"):
                dpg.show_item("tab_content_composition")
            self.current_tab = "composition"
        elif tab_name == "properties" and self.is_composition_normalized:
            if dpg.does_item_exist("tab_content_properties"):
                dpg.show_item("tab_content_properties")
            self.current_tab = "properties"
        elif tab_name == "bips" and self.is_composition_normalized:
            if dpg.does_item_exist("tab_content_bips"):
                dpg.show_item("tab_content_bips")
            self.current_tab = "bips"
        
        # Обновляем состояние кнопок
        self._update_tab_buttons()
    
    def _update_tab_buttons(self):
        """Обновление состояния кнопок вкладок"""
        if dpg.does_item_exist("tab_properties"):
            dpg.configure_item("tab_properties", enabled=self.is_composition_normalized)
        
        if dpg.does_item_exist("tab_bips"):
            dpg.configure_item("tab_bips", enabled=self.is_composition_normalized)
    
    def update_composition_summary(self):
        """Обновление сводки по составу"""
        composition_data = self.composition_editor.get_composition_data()
        total_components = len(composition_data)
        total_fraction = self.composition_editor.get_total_fraction()
        
        self.is_composition_normalized = self.composition_editor.is_composition_normalized()
        
        # Обновляем UI
        if dpg.does_item_exist("total_components"):
            dpg.set_value("total_components", f"Total Components: {total_components}")
        
        if dpg.does_item_exist("total_fraction"):
            dpg.set_value("total_fraction", f"Total Mole Fraction: {total_fraction:.4f}")
        
        if dpg.does_item_exist("normalized_status"):
            status = "Yes" if self.is_composition_normalized else "No"
            dpg.set_value("normalized_status", f"Normalized: {status}")
        
        if dpg.does_item_exist("tabs_status"):
            tabs_status = "Unlocked" if self.is_composition_normalized else "Locked"
            dpg.set_value("tabs_status", f"Additional Tabs: {tabs_status}")
        
        # Обновляем состояние кнопок вкладок
        self._update_tab_buttons()
        
        # Если состав не нормализован и мы не на вкладке состава, переключаемся обратно
        if not self.is_composition_normalized and self.current_tab != "composition":
            self.switch_tab("composition")
    
    def show_window(self):
        """Показать окно"""
        # Сброс состояния
        if dpg.does_item_exist("new_fluid_name"):
            dpg.set_value("new_fluid_name", "New_Fluid")
        if dpg.does_item_exist("new_fluid_desc"):
            dpg.set_value("new_fluid_desc", "")
        if dpg.does_item_exist("new_fluid_source"):
            dpg.set_value("new_fluid_source", "")
        
        self.composition_editor.clear_selected_components()
        self.is_composition_normalized = False
        self.current_tab = "composition"
        self.switch_tab("composition")
        self.update_composition_summary()
        
        dpg.show_item("new_fluid_window")
    
    def hide_window(self):
        """Скрыть окно"""
        dpg.hide_item("new_fluid_window")
    
    def save_fluid(self):
        """Сохранение флюида"""
        if self.save_callback:
            self.save_callback()
    
    def get_fluid_data(self):
        """Получение данных флюида"""
        name = dpg.get_value("new_fluid_name") if dpg.does_item_exist("new_fluid_name") else "New_Fluid"
        description = dpg.get_value("new_fluid_desc") if dpg.does_item_exist("new_fluid_desc") else ""
        source = dpg.get_value("new_fluid_source") if dpg.does_item_exist("new_fluid_source") else ""
        
        return {
            "name": name,
            "description": description,
            "source": source,
            "composition": self.composition_editor.get_composition_data(),
            "correlations": self.properties_editor.get_correlation_methods(),
            "mixing_rule": self.properties_editor.get_mixing_rule(),
            "bips": self.bips_editor.get_bips_matrix(),
            "type": "Custom",
            "components": len(self.composition_editor.get_composition_data()),
            "mw": 0.0,
        }