# composition_editor.py
import dearpygui.dearpygui as dpg
from typing import List, Dict, Any

class CompositionEditor:
    """Редактор состава флюида"""
    
    def __init__(self, component_manager):
        self.component_manager = component_manager
        self.on_composition_change = None  # Callback для изменений
    
    def setup_editor(self, parent):
        """Настройка редактора состава"""
        with dpg.group(parent=parent):
            dpg.add_text("Composition Editor", color=(0, 200, 255))
            self._setup_templates_section()
            dpg.add_separator()
            self._setup_component_selector()
    
    def _setup_templates_section(self):
        """Секция шаблонов и импорта"""
        with dpg.group(horizontal=True):
            # Шаблоны
            with dpg.group(width=200):
                dpg.add_text("Templates", color=(200, 200, 0))
                dpg.add_button(
                    label="C20+ Template", 
                    callback=lambda: self.apply_composition_template("C20"),
                    width=180
                )
                dpg.add_button(
                    label="C36+ Template", 
                    callback=lambda: self.apply_composition_template("C36"),
                    width=180
                )
            
            # Импорт
            with dpg.group(width=200):
                dpg.add_text("Import", color=(200, 200, 0))
                dpg.add_button(
                    label="Excel", 
                    callback=self.excel_import,
                    width=180
                )
    
    def _setup_component_selector(self):
        """Селектор компонентов"""
        with dpg.group(horizontal=True, height=-1):
            # Панель доступных компонентов
            with dpg.child_window(width=300):
                self._setup_available_components_panel()
            
            # Таблица выбранных компонентов
            with dpg.child_window():
                self._setup_selected_components_table()
    
    def _setup_available_components_panel(self):
        """Панель доступных компонентов"""
        dpg.add_text("Available Components", color=(200, 200, 0))
        dpg.add_input_text(
            tag="component_search", 
            hint="Search components...", 
            width=-1, 
            callback=self.filter_components
        )
        
        with dpg.child_window(height=-60, tag="components_list_container"):
            self._setup_components_list()
        
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Add Selected", 
                callback=self.add_selected_components, 
                width=140
            )
            dpg.add_button(
                label="Select All", 
                callback=self.select_all_components, 
                width=140
            )
    
    def _setup_components_list(self):
        """Список компонентов с чекбоксами"""
        if dpg.does_item_exist("components_list_container"):
            for child in dpg.get_item_children("components_list_container", 1):
                dpg.delete_item(child)
        
        for component in self.component_manager.all_components:
            dpg.add_checkbox(
                label=component, 
                tag=f"comp_check_{component}",
                parent="components_list_container"
            )
    
    def _setup_selected_components_table(self):
        """Таблица выбранных компонентов"""
        dpg.add_text("Selected Components", color=(200, 200, 0))
        
        with dpg.table(
            tag="selected_components_table", 
            header_row=True, 
            borders_innerH=True, 
            borders_outerH=True,
            resizable=True, 
            reorderable=True, 
            height=-1, 
            width=-1,
            policy=dpg.mvTable_SizingStretchProp
        ):
            dpg.add_table_column(label="Component", width_stretch=True, init_width_or_weight=0.4)
            dpg.add_table_column(label="Mole Fraction", width_stretch=True, init_width_or_weight=0.4)
            dpg.add_table_column(label="Action", width_stretch=True, init_width_or_weight=0.2)

    # Основные методы бизнес-логики
    def apply_composition_template(self, cutoff):
        """Применение шаблона состава"""
        self.clear_selected_components()
        
        components_to_add = self.component_manager.get_hydrocarbon_template(cutoff)
        for component in components_to_add:
            self.add_component_to_table(component, 0.0)
        
        self.update_available_components()
        self._trigger_composition_change()
    
    def add_component_to_table(self, component, fraction=0.0):
        """Добавление компонента в таблицу"""
        table = "selected_components_table"
        if not dpg.does_item_exist(table):
            return
        
        # Проверка на дубликаты
        for child in dpg.get_item_children(table, 1):
            row_children = dpg.get_item_children(child, 1)
            if len(row_children) >= 1:
                existing_component = dpg.get_value(row_children[0])
                if existing_component == component:
                    return
        
        row_id = self.component_manager.get_next_row_id()
        
        with dpg.table_row(parent=table, tag=f"selected_row_{row_id}"):
            dpg.add_text(component, tag=f"selected_comp_{row_id}")
            dpg.add_input_float(
                tag=f"selected_frac_{row_id}", 
                default_value=fraction, 
                step=0.01, 
                format="%.4f", 
                width=-1,
                callback=self._trigger_composition_change
            )
            dpg.add_button(
                label="Remove", 
                tag=f"selected_remove_{row_id}",
                callback=lambda s, d, idx=row_id: self.remove_selected_component(idx),
                width=-1
            )
    
    def remove_selected_component(self, row_index):
        """Удаление выбранного компонента"""
        if dpg.does_item_exist(f"selected_row_{row_index}"):
            dpg.delete_item(f"selected_row_{row_index}")
            self.update_available_components()
            self._trigger_composition_change()
    
    def clear_selected_components(self):
        """Очистка всех выбранных компонентов"""
        table = "selected_components_table"
        if dpg.does_item_exist(table):
            for child in dpg.get_item_children(table, 1):
                dpg.delete_item(child)
            self.update_available_components()
            self._trigger_composition_change()
    
    def update_available_components(self):
        """Обновление списка доступных компонентов"""
        added_components = self.get_added_components()
        search_term = dpg.get_value("component_search").lower() if dpg.does_item_exist("component_search") else ""
        
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if dpg.does_item_exist(checkbox_tag):
                if component in added_components:
                    dpg.hide_item(checkbox_tag)
                elif search_term in component.lower() or not search_term:
                    dpg.show_item(checkbox_tag)
                else:
                    dpg.hide_item(checkbox_tag)
    
    def get_added_components(self):
        """Получение добавленных компонентов"""
        added_components = []
        table = "selected_components_table"
        
        if dpg.does_item_exist(table):
            for child in dpg.get_item_children(table, 1):
                row_children = dpg.get_item_children(child, 1)
                if len(row_children) >= 1:
                    component = dpg.get_value(row_children[0])
                    added_components.append(component)
        
        return added_components
    
    def get_composition_data(self):
        """Получение данных о составе"""
        composition_data = []
        table = "selected_components_table"
        
        if dpg.does_item_exist(table):
            for child in dpg.get_item_children(table, 1):
                row_children = dpg.get_item_children(child, 1)
                if len(row_children) >= 2:
                    component = dpg.get_value(row_children[0])
                    fraction = dpg.get_value(row_children[1])
                    if component and fraction is not None:
                        composition_data.append({
                            "component": component,
                            "fraction": fraction
                        })
        
        return composition_data
    
    def get_total_fraction(self):
        """Получение суммарной мольной доли"""
        total = 0.0
        for comp_data in self.get_composition_data():
            total += comp_data["fraction"]
        return total
    
    def is_composition_normalized(self):
        """Проверка нормализации состава"""
        return abs(self.get_total_fraction() - 1.0) < 0.0001
    
    def _trigger_composition_change(self):
        """Триггер изменения состава"""
        if self.on_composition_change:
            self.on_composition_change()
    
    def filter_components(self):
        """Фильтрация компонентов"""
        self.update_available_components()
    
    def add_selected_components(self):
        """Добавление выбранных компонентов"""
        selected_components = []
        
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if dpg.does_item_exist(checkbox_tag) and dpg.get_value(checkbox_tag):
                selected_components.append(component)
        
        for component in selected_components:
            self.add_component_to_table(component)
        
        self.reset_component_checkboxes()
        self.update_available_components()
        self._trigger_composition_change()
    
    def select_all_components(self):
        """Выбор всех компонентов"""
        added_components = self.get_added_components()
        
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if (dpg.does_item_exist(checkbox_tag) and 
                dpg.is_item_visible(checkbox_tag) and 
                component not in added_components):
                dpg.set_value(checkbox_tag, True)
    
    def reset_component_checkboxes(self):
        """Сброс чекбоксов"""
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if dpg.does_item_exist(checkbox_tag):
                dpg.set_value(checkbox_tag, False)
    
    def auto_fill_fractions(self):
        """Автозаполнение долей"""
        table = "selected_components_table"
        if not dpg.does_item_exist(table):
            return
        
        component_count = len(dpg.get_item_children(table, 1))
        if component_count > 0:
            fraction_value = 1.0 / component_count
            for child in dpg.get_item_children(table, 1):
                row_children = dpg.get_item_children(child, 1)
                if len(row_children) >= 2:
                    dpg.set_value(row_children[1], fraction_value)
        
        self._trigger_composition_change()
    
    def auto_normalize(self):
        """Автонормализация"""
        table = "selected_components_table"
        if not dpg.does_item_exist(table):
            return
        
        total_fraction = 0.0
        fraction_items = []
        
        for child in dpg.get_item_children(table, 1):
            row_children = dpg.get_item_children(child, 1)
            if len(row_children) >= 2:
                fraction_value = dpg.get_value(row_children[1])
                if fraction_value is not None:
                    total_fraction += fraction_value
                    fraction_items.append(row_children[1])
        
        if total_fraction > 0 and abs(total_fraction - 1.0) > 0.0001:
            for fraction_item in fraction_items:
                current_value = dpg.get_value(fraction_item)
                if current_value is not None:
                    dpg.set_value(fraction_item, current_value / total_fraction)
        
        self._trigger_composition_change()
    
    def check_validity(self):
        """Проверка валидности"""
        table = "selected_components_table"
        if not dpg.does_item_exist(table):
            return
        
        total_fraction = 0.0
        has_errors = False
        error_messages = []
        
        for child in dpg.get_item_children(table, 1):
            row_children = dpg.get_item_children(child, 1)
            if len(row_children) >= 2:
                component_value = dpg.get_value(row_children[0])
                fraction_value = dpg.get_value(row_children[1])
                
                if fraction_value is None or fraction_value < 0:
                    error_messages.append(f"Invalid fraction for {component_value}")
                    has_errors = True
                else:
                    total_fraction += fraction_value
        
        if abs(total_fraction - 1.0) > 0.0001:
            error_messages.append(f"Total mole fraction is {total_fraction:.4f}, should be 1.0")
            has_errors = True
        
        if has_errors:
            error_text = "Validation Errors:\n" + "\n".join(error_messages)
            self._show_message("Validation Failed", error_text)
        else:
            self._show_message("Validation Successful", "Composition is valid!")
    
    def _show_message(self, title, message):
        """Показать сообщение"""
        with dpg.window(label=title, modal=True, show=True, tag="message_window"):
            dpg.add_text(message)
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("message_window"))
    
    def excel_import(self):
        """Импорт из Excel"""
        with dpg.window(label="Excel Import", modal=True, show=True, tag="excel_import_window",
                       width=500, height=300):
            dpg.add_text("Excel Import Feature", color=(0, 200, 255))
            dpg.add_text("This feature is under development and will be available in the next update.", 
                       color=(200, 200, 0))
            dpg.add_separator()
            dpg.add_text("Planned functionality:", color=(200, 200, 0))
            dpg.add_text("• Import composition from Excel files")
            dpg.add_text("• Support for .xlsx and .xls formats") 
            dpg.add_text("• Automatic component recognition")
            dpg.add_text("• Mole fraction validation")
            dpg.add_separator()
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("excel_import_window"), width=480)