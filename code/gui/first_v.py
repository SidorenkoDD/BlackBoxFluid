import dearpygui.dearpygui as dpg
from typing import List, Dict, Any, Optional

class ThemeManager:
    """Управление темами приложения"""
    
    @staticmethod
    def setup_global_theme():
        """Настройка глобальной темы"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 6, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
        
        dpg.bind_theme(global_theme)

class FluidDatabase:
    """Управление базой данных флюидов"""
    
    def __init__(self):
        self.fluids: List[Dict[str, Any]] = []
        self.current_fluid: Optional[Dict[str, Any]] = None
        self.load_fluids()
    
    def load_fluids(self):
        """Загрузка флюидов из базы данных"""
        # Заглушка - в реальности загружаем из JSON файла
        self.fluids = [
            {"name": "North Sea Oil", "type": "Black Oil", "components": 8, "mw": 125.4, "date": "2024-01-15"},
            {"name": "Gas Condensate", "type": "Gas Condensate", "components": 12, "mw": 89.2, "date": "2024-01-10"},
            {"name": "Dry Gas Field", "type": "Dry Gas", "components": 6, "mw": 19.8, "date": "2024-01-05"}
        ]
    
    def add_fluid(self, fluid_data: Dict[str, Any]):
        """Добавление нового флюида"""
        self.fluids.append(fluid_data)
    
    def delete_fluid(self, index: int):
        """Удаление флюида по индексу"""
        if 0 <= index < len(self.fluids):
            del self.fluids[index]
    
    def copy_fluid(self, index: int) -> Dict[str, Any]:
        """Копирование флюида"""
        if 0 <= index < len(self.fluids):
            original = self.fluids[index].copy()
            original["name"] = f"{original['name']}_Copy"
            original["date"] = "2024-01-20"
            return original
        return {}

class ComponentManager:
    """Управление компонентами флюидов"""
    
    def __init__(self):
        self.all_components = self._get_all_components()
        self.next_row_index = 0
        self.hydrocarbon_components = self._get_hydrocarbon_components()
    
    def _get_all_components(self) -> List[str]:
        """Получение всех доступных компонентов"""
        base_components = ["C1", "C2", "C3", "iC4", "nC4", "iC5", "nC5", "C6", "C7+"]
        additional_components = [
            "N2", "CO2", "H2S", "H2", "O2", "CO", "H2O",
            "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15",
            "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25",
            "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35",
            "C36", "C37", "C38", "C39", "C40"
        ]
        return base_components + additional_components
    
    def _get_hydrocarbon_components(self) -> Dict[str, List[str]]:
        """Получение углеводородных компонентов для шаблонов"""
        # Углеводороды C1-C20
        c1_c20 = ["C1", "C2", "C3", "iC4", "nC4", "iC5", "nC5", "C6", "C7", 
                 "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", 
                 "C16", "C17", "C18", "C19", "C20"]
        
        # Углеводороды C1-C36
        c1_c36 = c1_c20 + ["C21", "C22", "C23", "C24", "C25", "C26", "C27", 
                          "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36"]
        
        return {
            "C20": c1_c20,
            "C36": c1_c36
        }
    
    def get_hydrocarbon_template(self, template_name: str) -> List[str]:
        """Получение шаблона углеводородов"""
        return self.hydrocarbon_components.get(template_name, [])

class FluidCompositionEditor:
    """Редактор состава флюида"""
    
    def __init__(self, component_manager: ComponentManager, save_callback=None):
        self.component_manager = component_manager
        self.save_callback = save_callback
        self.current_tab = "composition"
        self.is_composition_normalized = False
        self.setup_window()
    
    def setup_window(self):
        """Настройка окна редактора состава"""
        with dpg.window(
            label="Create New Fluid", 
            tag="new_fluid_window", 
            width=1000, 
            height=700, 
            show=False, 
            modal=True,
            on_close=self.hide_window,
            no_resize=True
        ):
            # Главный контейнер с горизонтальным layout
            with dpg.group(horizontal=True, height=-1):
                # Левая панель - основные параметры (фиксированная ширина)
                with dpg.child_window(width=300):
                    self._setup_main_info_panel()
                
                # Правая панель - состав (растягивается)
                with dpg.child_window():
                    self._setup_tab_system()
    
    def _setup_tab_system(self):
        """Система вкладок для редактора флюида"""
        # Панель переключения вкладок
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
        
        # Контейнеры для вкладок
        with dpg.group(width=-1, height=-1):
            # Вкладка Composition Editor
            with dpg.child_window(
                tag="tab_content_composition", 
                show=True, 
                width=-1, 
                height=-1
            ):
                self._setup_composition_editor_tab()
            
            # Вкладка Properties & Correlations
            with dpg.child_window(
                tag="tab_content_properties", 
                show=False, 
                width=-1, 
                height=-1
            ):
                self._setup_properties_tab()
            
            # Вкладка BIPS
            with dpg.child_window(
                tag="tab_content_bips", 
                show=False, 
                width=-1, 
                height=-1
            ):
                self._setup_bips_tab()
    
    def switch_tab(self, tab_name):
        """Переключение между вкладками"""
        # Скрываем все вкладки
        for tab in ["composition", "properties", "bips"]:
            if dpg.does_item_exist(f"tab_content_{tab}"):
                dpg.hide_item(f"tab_content_{tab}")
        
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
    
    def _setup_composition_editor_tab(self):
        """Вкладка редактора состава"""
        dpg.add_text("Composition Editor", color=(0, 200, 255))
        self._setup_templates_section()
        dpg.add_separator()
        self._setup_component_selector()
    
    def _setup_properties_tab(self):
        """Вкладка свойств и корреляций"""
        dpg.add_text("Properties & Correlations", color=(0, 200, 255))
        dpg.add_text("Component Properties Configuration", color=(200, 200, 0))
        
        # Заглушка для свойств компонентов
        with dpg.group():
            dpg.add_text("Critical properties correlation methods:")
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True):
                dpg.add_table_column(label="Property")
                dpg.add_table_column(label="Correlation Method")
                
                properties = [
                    ("Critical Temperature", "Twu (1984)"),
                    ("Critical Pressure", "Twu (1984)"),
                    ("Acentric Factor", "Lee-Kesler (1975)"),
                    ("Molecular Weight", "Katz-Firoozabadi (1978)"),
                    ("Vapor Pressure", "Lee-Kesler (1975)")
                ]
                
                for prop_name, method in properties:
                    with dpg.table_row():
                        dpg.add_text(prop_name)
                        dpg.add_combo(
                            items=[method, "Soave (1972)", "Peng-Robinson (1976)", "Custom"],
                            default_value=method,
                            width=200
                        )
        
        dpg.add_separator()
        dpg.add_text("Mixing Rules", color=(200, 200, 0))
        with dpg.group(horizontal=True):
            dpg.add_radio_button(
                items=["Van der Waals", "Modified Huron-Vidal", "Wong-Sandler"],
                default_value="Van der Waals",
                tag="mixing_rules"
            )
    
    def _setup_bips_tab(self):
        """Вкладка BIPS (Binary Interaction Parameters)"""
        dpg.add_text("Binary Interaction Parameters (BIPS)", color=(0, 200, 255))
        dpg.add_text("Configure interaction parameters between components", color=(200, 200, 0))
        
        # Заглушка для BIPS
        with dpg.group():
            dpg.add_text("BIP Matrix (currently using default values):")
            
            # Таблица BIPS (упрощенная версия)
            with dpg.table(
                header_row=True, 
                borders_innerH=True, 
                borders_outerH=True,
                height=300,
                width=-1
            ):
                # Первый столбец - названия компонентов
                dpg.add_table_column(label="Component")
                
                # Добавляем столбцы для нескольких компонентов
                sample_components = ["C1", "C2", "C3", "nC4", "nC5", "C6", "C7+", "CO2", "N2"]
                for comp in sample_components:
                    dpg.add_table_column(label=comp)
                
                # Добавляем строки с данными
                for i, comp1 in enumerate(sample_components):
                    with dpg.table_row():
                        dpg.add_text(comp1)
                        for j, comp2 in enumerate(sample_components):
                            if i == j:
                                dpg.add_text("0.000")
                            else:
                                dpg.add_input_float(
                                    default_value=0.0,
                                    step=0.001,
                                    format="%.3f",
                                    width=60
                                )
        
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Reset to Defaults", width=120)
            dpg.add_button(label="Calculate Optimal BIPS", width=150)
            dpg.add_button(label="Import BIPS Matrix", width=120)
    
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
            ("Auto-Fill Fractions", "btn_auto_fill", self.auto_fill_fractions),
            ("Auto-Normalize", "btn_auto_normalize", self.auto_normalize),
            ("Check Validity", "btn_check_validity", self.check_validity),
            ("Clear All Components", "btn_clear_selected", self.clear_selected_components)
        ]
        
        for label, tag, callback in tools:
            dpg.add_button(label=label, tag=tag, callback=callback, width=280)
    
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
                tag="btn_save_fluid", 
                callback=self.save_fluid, 
                width=135
            )
            dpg.add_button(
                label="Cancel", 
                tag="btn_cancel_fluid", 
                callback=self.hide_window, 
                width=135
            )
    
    def _setup_templates_section(self):
        """Секция шаблонов и импорта"""
        with dpg.group(horizontal=True):
            # Шаблоны
            with dpg.group(width=200):
                dpg.add_text("Templates", color=(200, 200, 0))
                dpg.add_button(
                    label="C20+ Template", 
                    tag="btn_c20_template",
                    callback=lambda: self.apply_composition_template("C20"),
                    width=180
                )
                dpg.add_button(
                    label="C36+ Template", 
                    tag="btn_c36_template",
                    callback=lambda: self.apply_composition_template("C36"),
                    width=180
                )
            
            # Импорт
            with dpg.group(width=200):
                dpg.add_text("Import", color=(200, 200, 0))
                dpg.add_button(
                    label="Excel", 
                    tag="btn_excel_import",
                    callback=self.excel_import,
                    width=180
                )
    
    def _setup_component_selector(self):
        """Селектор компонентов - занимает всю доступную высоту"""
        # Главный контейнер для селектора компонентов
        with dpg.group(horizontal=True, height=-1):
            # Панель доступных компонентов (фиксированная ширина)
            with dpg.child_window(width=300):
                self._setup_available_components_panel()
            
            # Таблица выбранных компонентов (растягивается)
            with dpg.child_window():
                self._setup_selected_components_table()
    
    def _setup_available_components_panel(self):
        """Панель доступных компонентов - занимает всю высоту"""
        dpg.add_text("Available Components", color=(200, 200, 0))
        dpg.add_input_text(tag="component_search", hint="Search components...", 
                         width=-1, callback=self.filter_components)
        
        # Контейнер списка компонентов - растягивается по высоте, но оставляет место для кнопок
        with dpg.child_window(height=-60, tag="components_list_container"):
            self.setup_components_list()
        
        # Кнопки управления - внизу
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Add Selected", 
                tag="btn_add_selected",
                callback=self.add_selected_components, 
                width=140
            )
            dpg.add_button(
                label="Select All", 
                tag="btn_select_all",
                callback=self.select_all_components, 
                width=140
            )
    
    def _setup_selected_components_table(self):
        """Таблица выбранных компонентов - занимает всю доступную область"""
        dpg.add_text("Selected Components", color=(200, 200, 0))
        
        # Таблица растягивается на всю доступную высоту и ширину
        with dpg.table(tag="selected_components_table", header_row=True, 
                      borders_innerH=True, borders_outerH=True,
                      resizable=True, reorderable=True, 
                      height=-1, width=-1, policy=dpg.mvTable_SizingStretchProp):
            # Только три столбца - убрали лишний пустой столбец
            dpg.add_table_column(label="Component", width_stretch=True, init_width_or_weight=0.4)
            dpg.add_table_column(label="Mole Fraction", width_stretch=True, init_width_or_weight=0.4)
            dpg.add_table_column(label="Action", width_stretch=True, init_width_or_weight=0.2)

    def setup_components_list(self):
        """Настройка списка компонентов"""
        if dpg.does_item_exist("components_list_container"):
            for child in dpg.get_item_children("components_list_container", 1):
                dpg.delete_item(child)
        
        for component in self.component_manager.all_components:
            dpg.add_checkbox(
                label=component, 
                tag=f"comp_check_{component}",
                parent="components_list_container"
            )

    def apply_composition_template(self, cutoff):
        """Применить шаблон состава с заданным cutoff (только углеводороды)"""
        # Очищаем текущий состав
        self.clear_selected_components()
        
        # Получаем углеводородные компоненты для шаблона
        components_to_add = self.component_manager.get_hydrocarbon_template(cutoff)
        
        # Добавляем компоненты в таблицу с нулевыми долями
        for component in components_to_add:
            self.add_component_to_table(component, 0.0)
        
        # Обновляем список доступных компонентов
        self.update_available_components()
        
        self.show_message("Template Applied", 
                         f"Hydrocarbon composition template with cutoff {cutoff}+ has been applied")

    def filter_components(self):
        """Фильтрация компонентов"""
        added_components = self.get_added_components()
        search_term = dpg.get_value("component_search").lower()
        
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
        """Получить добавленные компоненты"""
        added_components = []
        table = "selected_components_table"
        
        if dpg.does_item_exist(table):
            for child in dpg.get_item_children(table, 1):
                row_children = dpg.get_item_children(child, 1)
                if len(row_children) >= 1:
                    component = dpg.get_value(row_children[0])
                    added_components.append(component)
        
        return added_components

    def add_selected_components(self):
        """Добавить выбранные компоненты"""
        selected_components = []
        
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if dpg.does_item_exist(checkbox_tag) and dpg.get_value(checkbox_tag):
                selected_components.append(component)
        
        for component in selected_components:
            self.add_component_to_table(component)
        
        self.reset_component_checkboxes()
        self.update_available_components()
        self.update_composition_summary()

    def add_component_to_table(self, component, fraction=0.0):
        """Добавить компонент в таблицу"""
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
        
        row_id = self.component_manager.next_row_index
        self.component_manager.next_row_index += 1
        
        with dpg.table_row(parent=table, tag=f"selected_row_{row_id}"):
            dpg.add_text(component, tag=f"selected_comp_{row_id}")
            dpg.add_input_float(tag=f"selected_frac_{row_id}", default_value=fraction, 
                              step=0.01, format="%.4f", width=-1,
                              callback=self.update_composition_summary)
            dpg.add_button(label="Remove", tag=f"selected_remove_{row_id}",
                         callback=lambda s, d, idx=row_id: self.remove_selected_component(idx),
                         width=-1)

    def remove_selected_component(self, row_index):
        """Удалить выбранный компонент"""
        if dpg.does_item_exist(f"selected_row_{row_index}"):
            dpg.delete_item(f"selected_row_{row_index}")
            self.update_available_components()
            self.update_composition_summary()

    def clear_selected_components(self):
        """Очистить выбранные компоненты"""
        table = "selected_components_table"
        if dpg.does_item_exist(table):
            for child in dpg.get_item_children(table, 1):
                dpg.delete_item(child)
            self.component_manager.next_row_index = 0
            self.update_available_components()
            self.update_composition_summary()

    def update_available_components(self):
        """Обновить доступные компоненты"""
        added_components = self.get_added_components()
        
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if dpg.does_item_exist(checkbox_tag):
                if component in added_components:
                    dpg.hide_item(checkbox_tag)
                else:
                    search_term = dpg.get_value("component_search").lower()
                    if search_term in component.lower() or not search_term:
                        dpg.show_item(checkbox_tag)
                    else:
                        dpg.hide_item(checkbox_tag)

    def update_composition_summary(self):
        """Обновить сводку по составу"""
        table = "selected_components_table"
        if not dpg.does_item_exist(table):
            return
        
        total_components = 0
        total_fraction = 0.0
        
        for child in dpg.get_item_children(table, 1):
            total_components += 1
            row_children = dpg.get_item_children(child, 1)
            if len(row_children) >= 2:
                fraction_value = dpg.get_value(row_children[1])
                if fraction_value is not None:
                    total_fraction += fraction_value
        
        # Обновляем значения только если элементы существуют
        if dpg.does_item_exist("total_components"):
            dpg.set_value("total_components", f"Total Components: {total_components}")
        
        if dpg.does_item_exist("total_fraction"):
            dpg.set_value("total_fraction", f"Total Mole Fraction: {total_fraction:.4f}")
        
        # Проверяем нормализацию и обновляем статус вкладок
        self.is_composition_normalized = abs(total_fraction - 1.0) < 0.0001
        
        if dpg.does_item_exist("normalized_status"):
            dpg.set_value("normalized_status", "Normalized: Yes" if self.is_composition_normalized else "Normalized: No")
        
        if dpg.does_item_exist("tabs_status"):
            status_text = "Additional Tabs: Unlocked" if self.is_composition_normalized else "Additional Tabs: Locked"
            dpg.set_value("tabs_status", status_text)
        
        # Обновляем состояние кнопок вкладок
        if dpg.does_item_exist("tab_properties"):
            dpg.configure_item("tab_properties", enabled=self.is_composition_normalized)
        
        if dpg.does_item_exist("tab_bips"):
            dpg.configure_item("tab_bips", enabled=self.is_composition_normalized)
        
        # Если мы не на вкладке состава и состав стал ненормализованным, переключаемся обратно
        if self.current_tab != "composition" and not self.is_composition_normalized:
            self.switch_tab("composition")

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
        
        self.update_composition_summary()

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
        
        self.update_composition_summary()

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
            self.show_message("Validation Failed", error_text)
        else:
            self.show_message("Validation Successful", "Composition is valid!")

    def show_message(self, title, message):
        """Показать сообщение"""
        with dpg.window(label=title, modal=True, show=True, tag="message_window"):
            dpg.add_text(message)
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("message_window"))

    def select_all_components(self):
        """Выбрать все компоненты"""
        added_components = self.get_added_components()
        
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if (dpg.does_item_exist(checkbox_tag) and 
                dpg.is_item_visible(checkbox_tag) and 
                component not in added_components):
                dpg.set_value(checkbox_tag, True)

    def reset_component_checkboxes(self):
        """Сбросить чекбоксы"""
        for component in self.component_manager.all_components:
            checkbox_tag = f"comp_check_{component}"
            if dpg.does_item_exist(checkbox_tag):
                dpg.set_value(checkbox_tag, False)

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

    def show_window(self):
        """Показать окно редактора"""
        dpg.set_value("new_fluid_name", "New_Fluid")
        dpg.set_value("new_fluid_desc", "")
        dpg.set_value("new_fluid_source", "")
        dpg.set_value("component_search", "")
        
        self.clear_selected_components()
        self.filter_components()
        self.reset_component_checkboxes()
        
        # Сбрасываем состояние вкладок
        self.is_composition_normalized = False
        self.current_tab = "composition"
        self.switch_tab("composition")
        
        dpg.show_item("new_fluid_window")
        dpg.focus_item("new_fluid_window")

    def hide_window(self):
        """Скрыть окно редактора"""
        dpg.hide_item("new_fluid_window")

    def save_fluid(self):
        """Сохранить флюид"""
        if self.save_callback:
            self.save_callback()

class FluidSidebar:
    """Боковая панель со списком флюидов"""
    
    def __init__(self, fluid_db: FluidDatabase, show_new_fluid_callback=None):
        self.fluid_db = fluid_db
        self.show_new_fluid_callback = show_new_fluid_callback
        self.setup_sidebar()
        self.refresh_fluids_list()
    
    def setup_sidebar(self):
        """Настройка боковой панели"""
        dpg.add_text("Fluids Database", color=(0, 200, 255))
        
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="fluid_search", hint="Search fluids...", width=250)
            dpg.add_button(label="Search", callback=self.search_fluids)
        
        dpg.add_separator()
        dpg.add_text("Available Fluids:")
        self.setup_fluids_accordion()
        dpg.add_separator()
        dpg.add_button(label="+ New Fluid", tag="btn_new_fluid", 
                      callback=self.show_new_fluid_window, width=330, height=30)
    
    def setup_fluids_accordion(self):
        """Настройка аккордеона флюидов"""
        with dpg.child_window(height=400, tag="fluids_accordion_container"):
            dpg.add_text("No fluids available", tag="no_fluids_text")
    
    def refresh_fluids_list(self):
        """Обновление списка флюидов"""
        if dpg.does_item_exist("fluids_accordion_container"):
            dpg.delete_item("fluids_accordion_container")
        
        with dpg.child_window(height=400, tag="fluids_accordion_container", parent="fluids_sidebar"):
            if not self.fluid_db.fluids:
                dpg.add_text("No fluids available", tag="no_fluids_text")
                return
            
            for i, fluid in enumerate(self.fluid_db.fluids):
                with dpg.collapsing_header(
                    label=fluid["name"], 
                    tag=f"fluid_header_{i}",
                    default_open=False,
                    closable=False
                ):
                    with dpg.group():
                        dpg.add_text(f"Type: {fluid['type']}", color=(200, 200, 0))
                        dpg.add_text(f"Components: {fluid['components']}")
                        dpg.add_text(f"Molecular Weight: {fluid['mw']}")
                        dpg.add_text(f"Date: {fluid['date']}")
                        
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Select", 
                                tag=f"btn_select_{i}",
                                callback=lambda s, d, idx=i: self.on_fluid_selected(idx),
                                width=80
                            )
                            dpg.add_button(
                                label="Copy", 
                                tag=f"btn_copy_{i}",
                                callback=lambda s, d, idx=i: self.copy_fluid(idx),
                                width=60
                            )
                            dpg.add_button(
                                label="Delete", 
                                tag=f"btn_delete_{i}",
                                callback=lambda s, d, idx=i: self.delete_fluid(idx),
                                width=60
                            )
    
    def search_fluids(self):
        """Поиск флюидов"""
        search_term = dpg.get_value("fluid_search")
        # Реализация поиска
        print(f"Searching for: {search_term}")

    def on_fluid_selected(self, index):
        """Обработчик выбора флюида"""
        if index < len(self.fluid_db.fluids):
            fluid = self.fluid_db.fluids[index]
            self.fluid_db.current_fluid = fluid
            
            dpg.set_value("info_name", fluid["name"])
            dpg.set_value("info_type", fluid["type"])
            dpg.set_value("info_components", str(fluid["components"]))
            dpg.set_value("info_mw", str(fluid["mw"]))
            dpg.set_value("info_date", fluid["date"])
            
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
        if index < len(self.fluid_db.fluids):
            fluid_name = self.fluid_db.fluids[index]["name"]
            
            # Создаем окно подтверждения с правильным содержимым
            with dpg.window(
                label="Confirm Delete", 
                modal=True, 
                show=True, 
                tag="confirm_delete_window",
                width=400,
                height=150
            ):
                dpg.add_text(f"Are you sure you want to delete '{fluid_name}'?")
                dpg.add_spacer(height=10)
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Yes", 
                        callback=lambda: self.confirm_delete(index),
                        width=100
                    )
                    dpg.add_button(
                        label="No", 
                        callback=lambda: dpg.delete_item("confirm_delete_window"),
                        width=100
                    )
    
    def confirm_delete(self, index):
        """Подтверждение удаления - исправленная версия"""
        # Удаляем окно подтверждения перед выполнением операции
        if dpg.does_item_exist("confirm_delete_window"):
            dpg.delete_item("confirm_delete_window")
        
        # Удаляем флюид
        self.fluid_db.delete_fluid(index)
        
        # Обновляем состояние приложения
        if (self.fluid_db.current_fluid and 
            self.fluid_db.current_fluid not in self.fluid_db.fluids):
            self.fluid_db.current_fluid = None
            dpg.show_item("main_content_message")
            dpg.hide_item("fluid_info_group")
            dpg.hide_item("calculation_tabs")
        
        # Обновляем список флюидов
        self.refresh_fluids_list()
    
    def show_new_fluid_window(self):
        """Показать окно создания флюида"""
        if self.show_new_fluid_callback:
            self.show_new_fluid_callback()

class MainContent:
    """Основная область контента"""
    
    def __init__(self):
        self.setup_main_content()
    
    def setup_main_content(self):
        """Настройка основной области"""
        dpg.add_text("PVT Simulator", color=(0, 200, 255))
        dpg.add_text("Select a fluid from the sidebar to start working", 
                   color=(150, 150, 150), tag="main_content_message")
        
        with dpg.group(tag="fluid_info_group", show=False):
            dpg.add_separator()
            dpg.add_text("Selected Fluid Information", color=(0, 200, 255))
            
            with dpg.table(tag="fluid_info_table", header_row=True, 
                          borders_innerH=True, borders_outerH=True):
                dpg.add_table_column(label="Property")
                dpg.add_table_column(label="Value")
                
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
        
        with dpg.group(tag="calculation_tabs", show=False):
            with dpg.tab_bar():
                with dpg.tab(label="Properties"):
                    dpg.add_text("Fluid properties will be displayed here")
                with dpg.tab(label="Composition"):
                    dpg.add_text("Detailed composition analysis will be displayed here")
                with dpg.tab(label="Calculations"):
                    dpg.add_text("Calculation results will be displayed here")

class PVTCompositionManager:
    """Главный класс приложения PVT Simulator"""
    
    def __init__(self):
        # Инициализация компонентов
        self.fluid_db = FluidDatabase()
        self.component_manager = ComponentManager()
        
        # Настройка GUI
        self.setup_gui()
        
        # Создание редактора после инициализации GUI
        self.composition_editor = FluidCompositionEditor(
            self.component_manager, 
            save_callback=self._save_new_fluid
        )
    
    def setup_gui(self):
        """Настройка графического интерфейса"""
        dpg.create_context()
        
        dpg.create_viewport(
            title='PVT Simulator', 
            width=1400, 
            height=900,
            min_width=1000,
            min_height=700
        )
        
        ThemeManager.setup_global_theme()
        
        with dpg.window(tag="Primary Window", no_scrollbar=True):
            with dpg.group(horizontal=True):
                # Боковая панель
                with dpg.child_window(width=350, tag="fluids_sidebar"):
                    self.sidebar = FluidSidebar(
                        self.fluid_db, 
                        show_new_fluid_callback=self.show_new_fluid_window
                    )
                
                # Основная область
                with dpg.child_window(tag="main_content_area"):
                    self.main_content = MainContent()
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)
        dpg.maximize_viewport()
    
    def show_new_fluid_window(self):
        """Показать окно создания нового флюида"""
        self.composition_editor.show_window()
    
    def _save_new_fluid(self):
        """Сохранение нового флюида"""
        name = dpg.get_value("new_fluid_name")
        description = dpg.get_value("new_fluid_desc")
        source = dpg.get_value("new_fluid_source")
        
        components_data = []
        total_components = 0
        
        table = "selected_components_table"
        if dpg.does_item_exist(table):
            for child in dpg.get_item_children(table, 1):
                row_children = dpg.get_item_children(child, 1)
                if len(row_children) >= 2:
                    component_value = dpg.get_value(row_children[0])
                    fraction_value = dpg.get_value(row_children[1])
                    
                    if component_value and fraction_value is not None and fraction_value > 0:
                        components_data.append({
                            "component": component_value,
                            "fraction": fraction_value
                        })
                        total_components += 1
        
        new_fluid = {
            "name": name,
            "type": "Custom",
            "components": total_components,
            "mw": 0.0,
            "date": "2024-01-20",
            "description": description,
            "source": source,
            "composition": components_data
        }
        
        self.fluid_db.add_fluid(new_fluid)
        self.sidebar.refresh_fluids_list()
        self.composition_editor.hide_window()
    
    def run(self):
        """Запуск приложения"""
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = PVTCompositionManager()
    app.run()