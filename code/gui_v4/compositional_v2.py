import dearpygui.dearpygui as dpg
from flash_calculator import FlashCalculator
from constants import COMPONENTS
from CompositionsJSONReader import CompositionsJSONReader
from DBReader import DBReader

class CompositionalModule:
    def __init__(self, flash_calc: FlashCalculator):
        self.flash_calc = flash_calc
        self.compositions = Compositions()
        self.variants = CompositionVariants()
        self.flash_input = FlashInputWindow(flash_calc, self.show_flash_results)
        self.main_window_tag = "compositional_main_window"
        self.content_area_tag = "compositional_content_area"
        
    def show_compositional_interface(self):
        if not dpg.does_item_exist(self.main_window_tag):
            self.create_main_window()
        else:
            dpg.show_item(self.main_window_tag)
            dpg.focus_item(self.main_window_tag)
    
    def create_main_window(self):
        with dpg.window(
            label="Compositional Module",
            tag=self.main_window_tag,
            width=1200,
            height=800,
            show=True,
            on_close=lambda: dpg.hide_item(self.main_window_tag)
        ):
            with dpg.group(horizontal=True):
                # Боковое меню
                with dpg.child_window(width=200, border=True):
                    dpg.add_text("Compositional", color=(0, 200, 255))
                    dpg.add_separator()
                    
                    # dpg.add_button(label = 'Comonents Manager',
                    #                width= 180,
                    #                enabled= False)
                    
                    dpg.add_button(
                        label="Compositions Manager",
                        width=180,
                        callback=self.show_compositions
                    )

                    # dpg.add_button(
                    #     label="Composition Variants",
                    #     width=180,
                    #     callback=self.show_variants
                    # )

                    dpg.add_button(
                        label='Library',
                        width=180,
                        enabled=False
                    )

                    dpg.add_button(
                        label="Flash Calculation",
                        width=180,
                        callback=self.show_flash_input
                    )
                    dpg.add_button(
                        label="Close Module",
                        width=180,
                        #callback=lambda: dpg.hide_item(self.main_window_tag)
                    )

                
                # Область контента
                with dpg.child_window(tag=self.content_area_tag, border=False):
                    dpg.add_text("Select an option from the left menu", pos=(300, 50))
    
    def show_compositions(self):
        self.hide_all_content()
        
        if not dpg.does_item_exist("compositions_window"):
            with dpg.child_window(
                parent=self.content_area_tag,
                label="Compositions Manager",
                tag="compositions_window",
                show=True,
                width=800,
                height=600
            ):
                self.compositions.create_interface()
        else:
            dpg.show_item("compositions_window")
            self.compositions.refresh_data()
    
    def show_variants(self):
        self.hide_all_content()
        
        if not dpg.does_item_exist("composition_variants_win"):
            with dpg.child_window(
                parent=self.content_area_tag,
                label="Composition Variants",
                tag="composition_variants_win",
                show=True,
                width=1000,
                height=600
            ):
                self.variants.create_interface()
        else:
            dpg.show_item("composition_variants_win")
            self.variants.refresh_data()


    def show_flash_input(self):
        self.hide_all_content()
        
        if not dpg.does_item_exist("flash_input_window"):
            with dpg.child_window(
                parent=self.content_area_tag,
                label="Flash Input Parameters",
                tag="flash_input_window",
                show=True,
                width=400,
                height=200
            ):
                self.flash_input.create_interface()
        else:
            dpg.show_item("flash_input_window")
    
    def show_flash_results(self):
        # Создаем окно результатов (можно адаптировать под ваш стиль)
        # if dpg.does_item_exist("flash_results_window"):
        #     dpg.delete_item("flash_results_window")
        #self.hide_all_content()

        results = self.flash_calc.calculate_flash()
        
        with dpg.window(
            label="Flash Calculation Results",
            tag="flash_results_window",
            width=600,
            height=400,
            modal=False
        ):
            dpg.add_input_text(
                multiline=True,
                height=350,
                width=580,
                default_value=results,
                readonly=True
            )
            
            # dpg.add_button(
            #     label="Close",
            #     callback=lambda: dpg.delete_item("flash_results_window"),
            #     pos=(250, 360)
            # )


    def hide_all_content(self):
        if dpg.does_item_exist("compositions_window"):
            dpg.hide_item("compositions_window")
        
        if dpg.does_item_exist("composition_variants_win"):
            dpg.hide_item("composition_variants_win")
        
        if dpg.does_item_exist("flash_input_window"):
            dpg.hide_item("flash_input_window")

        if dpg.does_item_exist("flash_results_window"):
            dpg.hide_item("flash_results_window")


class Compositions:
    def __init__(self):
        self.comp_reader = CompositionsJSONReader()
        self.current_composition = None
        self.initialized = False
    
    def create_interface(self):
        """Создает элементы интерфейса управления композициями"""
        # Верхняя часть с кнопками управления
        with dpg.group(horizontal=True):
            dpg.add_button(label="Add Composition", 
                         callback=self.show_add_composition_modal,
                         width=150, height=30)
        
        dpg.add_separator()
        
        # Основная часть с выпадающим списком и таблицей
        with dpg.group(horizontal=True):
            # Левая колонка - выпадающий список и информация
            with dpg.group(width=400):
                dpg.add_text("Available compositions:")
                self.compositions_combo = dpg.add_combo(
                    tag='compositions_combo',
                    callback=self.update_composition_display,
                    width=300
                )
                
                dpg.add_button(label="Edit Composition", 
                             callback=self.edit_composition_callback,
                             width=150, height=30)
                dpg.add_button(label="Delete Composition", 
                             callback=self.del_composition,
                             width=150, height=30)
                
                dpg.add_text("Composition Details:")
                dpg.add_text("Model Info:", indent=20)
                self.composition_info_text = dpg.add_text("", indent=40)
                
                dpg.add_text("Model Composition:", indent=20)
                self.composition_text = dpg.add_text("", indent=40)
            
            # Правая колонка - таблица с составом
            with dpg.group(width=400, tag="table_container"):
                pass
        
        self.refresh_data()
        self.initialized = True

    def refresh_data(self):
        """Обновляет данные в интерфейсе"""
        compositions = list(self.comp_reader.get_all_compositions_labels())
        
        if compositions:
            dpg.configure_item(self.compositions_combo, items=compositions)
            if not self.current_composition:
                default_comp = compositions[0]
                dpg.set_value(self.compositions_combo, default_comp)
                self.update_composition_display(None, default_comp)
        else:
            dpg.set_value(self.compositions_combo, "")
            dpg.set_value(self.composition_info_text, "")
            dpg.set_value(self.composition_text, "")
            self.update_composition_table({})

    def update_composition_display(self, sender, app_data):
        """Обновляет информацию о составе"""
        if not self.initialized:
            return
            
        selected_composition = dpg.get_value(self.compositions_combo)
        if not selected_composition:
            return
        
        self.current_composition = selected_composition
        
        dpg.set_value(self.composition_info_text, 
                     str(self.comp_reader.get_composition_info(selected_composition)))
        dpg.set_value(self.composition_text, 
                     str(self.comp_reader.get_composition(selected_composition)))
        
        composition_data = self.comp_reader.get_composition(selected_composition)
        self.update_composition_table(composition_data)

    def update_composition_table(self, composition_data):
        """Обновляет таблицу с составом"""
        if dpg.does_item_exist("composition_table"):
            dpg.delete_item("composition_table")
        
        if composition_data:
            with dpg.table(parent="table_container", tag="composition_table", 
                          header_row=True, borders_innerH=True, borders_outerH=True, 
                          borders_innerV=True, borders_outerV=True, width=300):
                dpg.add_table_column(label="Component", width_fixed=True)
                dpg.add_table_column(label="Mole Fraction", width_stretch=True)
                
                for component, value in composition_data.items():
                    with dpg.table_row():
                        dpg.add_text(component)
                        dpg.add_text(f"{value:.4f}")

    def show_add_composition_modal(self):
        if dpg.does_item_exist("add_composition_modal"):
            dpg.delete_item("add_composition_modal")

        with dpg.window(label="Add New Composition", modal=True, 
                       width=400, height=600, tag='add_composition_modal'):
            dpg.add_text("Enter composition:")
            dpg.add_input_text(label="Name", tag='new_composition_name')
            
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
                            user_data=component
                        )
            
            dpg.add_button(label="Save", callback=self.save_new_composition)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("add_composition_modal"))

    def save_new_composition(self):
        composition_name = dpg.get_value("new_composition_name")
        
        if not composition_name:
            print("Error: Composition name cannot be empty!")
            return
        
        composition = {}
        for component in COMPONENTS:
            input_tag = f"input_{component}"
            try:
                value = dpg.get_value(input_tag)
                if value is not None:
                    composition[component] = value
            except Exception as e:
                print(f"Error getting value for component {component}: {e}")
        
        if not any(composition.values()):
            print("Error: At least one component must have non-zero value!")
            return
        
        self.comp_reader.add_composition(composition_name=composition_name, composition=composition)
        
        if dpg.does_item_exist('compositions_combo'):
            new_compositions = list(self.comp_reader.get_all_compositions_labels())
            dpg.configure_item('compositions_combo', items=new_compositions)
            dpg.set_value('compositions_combo', composition_name)
            self.update_composition_display('compositions_combo', None)
        
        dpg.delete_item("add_composition_modal")

    def edit_composition_callback(self):
        current_comp = dpg.get_value('compositions_combo')
        if not current_comp:
            return
        
        composition_data = self.comp_reader.get_composition(current_comp)
        composition_info = self.comp_reader.get_composition_info(current_comp)
        
        if dpg.does_item_exist("edit_composition_modal"):
            dpg.delete_item("edit_composition_modal")

        with dpg.window(label="Edit Composition", modal=True, 
                    width=400, height=600, tag='edit_composition_modal'):
            dpg.add_text("Edit composition:")
            dpg.add_input_text(label="Name", tag='edit_composition_name', default_value=current_comp)
            
            dpg.add_text("Model Info:")
            dpg.add_input_text(multiline=True, tag='edit_composition_info', 
                            default_value=str(composition_info), width=400, height=100)
            
            with dpg.table(header_row=True):
                dpg.add_table_column(label='Component')
                dpg.add_table_column(label='Mole Fraction')
                
                for component in COMPONENTS:
                    with dpg.table_row():
                        dpg.add_text(component)
                        value = composition_data.get(component, 0.0)
                        dpg.add_input_float(
                            default_value=float(value),
                            tag=f"edit_input_{component}",
                            step=0.05,
                            user_data=component
                        )
            
            dpg.add_button(label="Save Changes", callback=lambda: self.save_edited_composition(current_comp))
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("edit_composition_modal"))

    def save_edited_composition(self, old_name):
        new_name = dpg.get_value("edit_composition_name")
        if not new_name:
            print("Error: Composition name cannot be empty!")
            return
        
        new_composition = {}
        for component in COMPONENTS:
            input_tag = f"edit_input_{component}"
            try:
                value = dpg.get_value(input_tag)
                if value is not None:
                    new_composition[component] = value
            except Exception as e:
                print(f"Error getting value for component {component}: {e}")
        
        if not any(new_composition.values()):
            print("Error: At least one component must have non-zero value!")
            return
        
        new_info = dpg.get_value("edit_composition_info")
        
        self.comp_reader.update_composition(
            old_name=old_name,
            new_name=new_name,
            new_composition=new_composition,
            new_info=new_info
        )
        
        new_compositions = list(self.comp_reader.get_all_compositions_labels())
        dpg.configure_item('compositions_combo', items=new_compositions)
        dpg.set_value('compositions_combo', new_name)
        self.update_composition_display('compositions_combo', None)
        
        dpg.delete_item("edit_composition_modal")

    def del_composition(self):
        comp_to_del = dpg.get_value('compositions_combo')
        self.comp_reader.del_composition(comp_to_del)
        
        new_compositions = list(self.comp_reader.get_all_compositions_labels())
        dpg.configure_item('compositions_combo', items=new_compositions)
        
        if new_compositions:
            dpg.set_value('compositions_combo', new_compositions[0])
            self.update_composition_display('compositions_combo', None)
        else:
            dpg.set_value('composition_info_text', "")
            dpg.set_value('composition_text', "")
            if dpg.does_item_exist("composition_table"):
                dpg.delete_item("composition_table")


class CompositionVariants:
    def __init__(self):
        self.table_data = []
        self.row_counter = 0
        self.compositions_db = CompositionsJSONReader()
        self.library_db = DBReader()
        self.initialized = False

    def create_interface(self):
        """Создает интерфейс для вариантов композиций"""
        self.main_table = dpg.add_table(
            tag="main_table", 
            header_row=True, 
            policy=dpg.mvTable_SizingStretchProp,
            borders_outerH=True, 
            borders_innerV=True, 
            borders_innerH=True, 
            borders_outerV=True,
            parent="composition_variants_win"
        )
        
        dpg.add_table_column(label="Composition", width_fixed=True, parent=self.main_table)
        dpg.add_table_column(label="EOS", parent=self.main_table)
        dpg.add_table_column(label="Shift Parameter", parent=self.main_table)
        dpg.add_table_column(label="Acentric Factor", parent=self.main_table)
        dpg.add_table_column(label="Critical P", parent=self.main_table)
        dpg.add_table_column(label="Critical T", parent=self.main_table)
        dpg.add_table_column(label="Calculate", width_fixed=True, parent=self.main_table)
        
        for _ in range(3):
            self.add_table_row()

        with dpg.group(horizontal=True):
            dpg.add_button(label="Add Row", callback=self.add_table_row)
            dpg.add_button(label="Remove Selected Row", callback=self.remove_table_row)
            dpg.add_button(label="Calculate Selected", callback=self.calculate_selected)
            dpg.add_button(label="Add selected composition to db", callback=self.add_composition_to_db)
        
        self.initialized = True

    def refresh_data(self):
        """Обновляет данные в интерфейсе"""
        if not self.initialized:
            return
            
        compositions = self.compositions_db.get_all_compositions_labels()
        shift_params = self.library_db.get_all_shift_labels()
        acentric_factors = self.library_db.get_all_acentric_factor_labels()
        critical_pressures = self.library_db.get_all_pcrit_labels()
        critical_temps = self.library_db.get_all_tcrit_labels()
        
        for i, row in enumerate(self.table_data):
            dpg.configure_item(row["composition"], items=compositions)
            dpg.configure_item(row["shift"], items=shift_params)
            dpg.configure_item(row["acentric"], items=acentric_factors)
            dpg.configure_item(row["crit_p"], items=critical_pressures)
            dpg.configure_item(row["crit_t"], items=critical_temps)

    def add_table_row(self):
        compositions = self.compositions_db.get_all_compositions_labels()
        eos_options = ["PR", "SRK", "RK", "VDW"]
        shift_params = self.library_db.get_all_shift_labels()
        acentric_factors = self.library_db.get_all_acentric_factor_labels()
        critical_pressures = self.library_db.get_all_pcrit_labels()
        critical_temps = self.library_db.get_all_tcrit_labels()
        
        with dpg.table_row(parent=self.main_table, tag=f"row_{self.row_counter}"):
            row_data = {
                "composition": dpg.add_combo(
                    items=compositions, 
                    default_value=compositions[0] if compositions else "", 
                    width=120, 
                    tag=f"comp_{self.row_counter}"
                ),
                "eos": dpg.add_combo(
                    items=eos_options, 
                    default_value=eos_options[0], 
                    width=80, 
                    tag=f"eos_{self.row_counter}"
                ),
                "shift": dpg.add_combo(
                    items=shift_params, 
                    default_value=shift_params[0] if shift_params else "", 
                    width=120, 
                    tag=f"shift_{self.row_counter}"
                ),
                "acentric": dpg.add_combo(
                    items=acentric_factors, 
                    default_value=acentric_factors[0] if acentric_factors else "", 
                    width=120, 
                    tag=f"acentric_{self.row_counter}"
                ),
                "crit_p": dpg.add_combo(
                    items=critical_pressures, 
                    default_value=critical_pressures[0] if critical_pressures else "", 
                    width=120, 
                    tag=f"crit_p_{self.row_counter}"
                ),
                "crit_t": dpg.add_combo(
                    items=critical_temps, 
                    default_value=critical_temps[0] if critical_temps else "", 
                    width=120, 
                    tag=f"crit_t_{self.row_counter}"
                ),
                "calculate": dpg.add_checkbox(
                    default_value=True, 
                    tag=f"calc_{self.row_counter}"
                )
            }
            
            self.table_data.append(row_data)
            self.row_counter += 1

    def remove_table_row(self):
        if not self.table_data:
            return
        
        selected_rows = []
        for i, row in enumerate(self.table_data):
            if dpg.get_value(f"calc_{i}"):
                selected_rows.append(i)
        
        for i in sorted(selected_rows, reverse=True):
            dpg.delete_item(f"row_{i}")
            self.table_data.pop(i)
        
        self.row_counter = len(self.table_data)
        
        for i, row in enumerate(self.table_data):
            for key in row:
                if key != "calculate":
                    new_tag = f"{key.split('_')[0]}_{i}"
                    dpg.configure_item(row[key], tag=new_tag)

    def calculate_selected(self):
        selected_rows = []
        for i, row in enumerate(self.table_data):
            if dpg.get_value(f"calc_{i}"):
                selected_rows.append({
                    "composition": dpg.get_value(f"comp_{i}"),
                    "eos": dpg.get_value(f"eos_{i}"),
                    "shift": dpg.get_value(f"shift_{i}"),
                    "acentric": dpg.get_value(f"acentric_{i}"),
                    "crit_p": dpg.get_value(f"crit_p_{i}"),
                    "crit_t": dpg.get_value(f"crit_t_{i}")
                })
        
        print("Selected for calculation:", selected_rows)

    def add_composition_to_db(self):
        data_to_save = []
        
        for i, row in enumerate(self.table_data):
            data_to_save.append({
                "composition": dpg.get_value(f"comp_{i}"),
                "eos": dpg.get_value(f"eos_{i}"),
                "shift_parameter": dpg.get_value(f"shift_{i}"),
                "acentric_factor": dpg.get_value(f"acentric_{i}"),
                "critical_pressure": dpg.get_value(f"crit_p_{i}"),
                "critical_temperature": dpg.get_value(f"crit_t_{i}"),
                "calculate": dpg.get_value(f"calc_{i}")
            })
        
        print(data_to_save)


class FlashInputWindow:
    def __init__(self, flash_calc: FlashCalculator, results_callback):
        self.db_compositions = CompositionsJSONReader()
        self.flash_calc = flash_calc
        self.results_callback = results_callback
        
    def create_interface(self):
        """Создает интерфейс ввода параметров флеш-расчета"""
        dpg.add_combo(label= 'Choose variant',items=self.db_compositions.get_all_compositions_labels())
        dpg.add_input_float(
            label='Pressure, bar',
            tag='input_pressure',
            default_value=self.flash_calc.pressure,
            callback=lambda s, a: self.flash_calc.update_pt(a, self.flash_calc.temperature),
            width=200
        )
        dpg.add_input_float(
            label='Temperature, °C',
            tag='input_temperature',
            default_value=self.flash_calc.temperature,
            callback=lambda s, a: self.flash_calc.update_pt(self.flash_calc.pressure, a),
            width=200
        )
        dpg.add_button(
            label='Calculate Flash',
            callback=self.results_callback,
            width=200
        )


def show_compositional_interface(flash_calc: FlashCalculator):
    """Функция для совместимости со старым кодом"""
    module = CompositionalModule(flash_calc)
    module.show_compositional_interface()
    return module