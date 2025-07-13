# compositional.py
import dearpygui.dearpygui as dpg
from flash_calculator import FlashCalculator
from constants import COMPONENTS, WINDOW_POSITIONS
from CompositionsJSONReader import CompositionsJSONReader
from DBReader import DBReader



class Compositions:
    def __init__(self):
        self.comp_reader = CompositionsJSONReader()
        self.current_composition = None

    def update_composition_display(self, sender, app_data):
        """Обновляет информацию о составе при изменении выбранной композиции"""
        selected_composition = dpg.get_value(sender)
        
        # Обновляем текстовые поля
        dpg.set_value("composition_info_text", str(self.comp_reader.get_composition_info(selected_composition)))
        dpg.set_value("composition_text", str(self.comp_reader.get_composition(selected_composition)))
        
        # Обновляем таблицу
        composition_data = self.comp_reader.get_composition(selected_composition)
        self.update_composition_table(composition_data)

    def update_composition_table(self, composition_data):
        """Обновляет таблицу с составом"""
        # Очищаем старую таблицу (если существует)
        if dpg.does_item_exist("composition_table"):
            dpg.delete_item("composition_table")
        
        # Создаем новую таблицу
        with dpg.table(parent="compositions_window", tag="composition_table", 
                      header_row=True, borders_innerH=True, borders_outerH=True, 
                      borders_innerV=True, borders_outerV=True, width=300):
            dpg.add_table_column(label="Component", width_fixed=True)
            dpg.add_table_column(label="Mole Fraction", width_stretch=True)
            
            for component, value in composition_data.items():
                with dpg.table_row():
                    dpg.add_text(component)
                    dpg.add_text(f"{value:.4f}")

    def create(self):
        if dpg.does_item_exist("compositions_window"):
            dpg.delete_item("compositions_window")

        with dpg.window(label="Compositions Manager", width=600, height=500, tag="compositions_window"):
            # Верхняя часть с кнопками управления
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add Composition", 
                             callback=self.show_add_composition_modal,
                             width=150, height=30)
                # dpg.add_button(label="Edit Composition", 
                #              callback=self.edit_composition_callback,
                #              width=150, height=30)
                # dpg.add_button(label="Delete Composition", 
                #              callback=self.delete_composition_callback,
                #              width=150, height=30)
            
            dpg.add_separator()
            
            # Основная часть с выпадающим списком и таблицей
            with dpg.group(horizontal=True):
                # Левая колонка - выпадающий список и информация
                with dpg.group(width=400):
                    dpg.add_text("Available compositions:")
                    compositions = list(self.comp_reader.get_all_compositions_labels())
                    
                    if compositions:
                        default_comp = compositions[0]
                        dpg.add_combo(compositions, tag='compositions_combo',
                                    default_value=default_comp,
                                    callback=self.update_composition_display,
                                    width=300)
                        dpg.add_button(label="Edit Composition", 
                             callback=self.edit_composition_callback,
                             width=150, height=30)
                        dpg.add_button(label="Delete Composition", 
                             callback=self.del_composition,
                             width=150, height=30)
                        dpg.add_text("Composition Details:")
                        dpg.add_text("Model Info:", indent=20)
                        dpg.add_text(str(self.comp_reader.get_composition_info(default_comp)), 
                                    tag="composition_info_text", indent=40)
                        
                        dpg.add_text("Model Composition:", indent=20)
                        dpg.add_text(str(self.comp_reader.get_composition(default_comp)), 
                                    tag="composition_text", indent=40)
                    else:
                        dpg.add_text("No compositions available")
                
                # Правая колонка - таблица с составом
                with dpg.group(width=400):
                    if compositions:
                        # Инициализируем таблицу с данными первой композиции
                        initial_data = self.comp_reader.get_composition(compositions[0])
                        self.update_composition_table(initial_data)

    def edit_composition_callback(self):
        current_comp = dpg.get_value('compositions_combo')
        if not current_comp:
            return
        
        # Получаем текущие данные композиции
        composition_data = self.comp_reader.get_composition(current_comp)
        composition_info = self.comp_reader.get_composition_info(current_comp)
        
        # Создаем модальное окно для редактирования
        if dpg.does_item_exist("edit_composition_modal"):
            dpg.delete_item("edit_composition_modal")

        with dpg.window(label="Edit Composition", no_close=False, modal=True, 
                    width=400, height=600, tag='edit_composition_modal'):
            dpg.add_text("Edit composition:")
            dpg.add_input_text(label="Name", tag='edit_composition_name', default_value=current_comp)
            
            # Добавляем информацию о модели (если нужно)
            dpg.add_text("Model Info:")
            dpg.add_input_text(multiline=True, tag='edit_composition_info', 
                            default_value=str(composition_info), width=400, height=100)
            
            # Таблица с компонентами
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
        
        # Собираем новые данные композиции
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
        
        # Получаем новую информацию о модели
        new_info = dpg.get_value("edit_composition_info")
        
        # Обновляем данные в JSON
        self.comp_reader.update_composition(
            old_name=old_name,
            new_name=new_name,
            new_composition=new_composition,
            new_info=new_info
        )
        
        # Обновляем интерфейс
        new_compositions = list(self.comp_reader.get_all_compositions_labels())
        dpg.configure_item('compositions_combo', items=new_compositions)
        dpg.set_value('compositions_combo', new_name)
        self.update_composition_display('compositions_combo', None)
        
        dpg.delete_item("edit_composition_modal")

    def del_composition(self):
        comp_to_del = dpg.get_value('compositions_combo')
        self.comp_reader.del_composition(comp_to_del)
        
        # Обновляем выпадающий список
        new_compositions = list(self.comp_reader.get_all_compositions_labels())
        dpg.configure_item('compositions_combo', items=new_compositions)
        
        # Если есть оставшиеся композиции, выбираем первую
        if new_compositions:
            dpg.set_value('compositions_combo', new_compositions[0])
            self.update_composition_display('compositions_combo', None)
        else:
            # Если композиций не осталось, очищаем поля
            dpg.set_value('composition_info_text', "")
            dpg.set_value('composition_text', "")
            if dpg.does_item_exist("composition_table"):
                dpg.delete_item("composition_table")

    def show_add_composition_modal(self):
        if dpg.does_item_exist("add_composition_modal"):
            dpg.delete_item("add_composition_modal")

        with dpg.window(label="Add New Composition", no_close=False, modal=True, 
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
                            callback=lambda s, a, u: self.flash_calc.update_composition(u, a),
                            user_data=component
                        )
            
            dpg.add_button(label="Save", callback=self.save_new_composition_v2)
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("add_composition_modal"))

    def save_new_composition_v2(self):
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
        
        print(f"Saving composition '{composition_name}': {composition}")
        
        if hasattr(self, 'comp_reader'):
            self.comp_reader.add_composition(composition_name=composition_name, composition=composition)
        
        if dpg.does_item_exist('compositions_combo'):
            new_compositions = list(self.comp_reader.get_all_compositions_labels())
            dpg.configure_item('compositions_combo', items=new_compositions)
            
            # Устанавливаем новую композицию как текущую
            dpg.set_value('compositions_combo', composition_name)
            self.update_composition_display('compositions_combo', None)
        
        dpg.delete_item("add_composition_modal")


class CompositionVariants:
    def __init__(self):
        self.table_data = []
        self.row_counter = 0
        self.compositions_db = CompositionsJSONReader()
        self.library_db = DBReader()



    def create_composition_variants_window(self):
        if dpg.does_item_exist("composition_variants_win"):
            dpg.delete_item("composition_variants_win")
    
        with dpg.window(label="Composition Variants", tag="composition_variants_win", width=1000, height=600):
            # Создаем таблицу
            with dpg.table(tag="main_table", header_row=True, policy=dpg.mvTable_SizingStretchProp,
                        borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True):
                # Добавляем колонки
                dpg.add_table_column(label="Composition", width_fixed=True)
                dpg.add_table_column(label="EOS")
                dpg.add_table_column(label="Shift Parameter")
                dpg.add_table_column(label="Acentric Factor")
                dpg.add_table_column(label="Critical P")
                dpg.add_table_column(label="Critical T")
                dpg.add_table_column(label="Calculate", width_fixed=True)
                
                # Добавляем начальные 3 строки
                for _ in range(3):
                    self.add_table_row()

            # Кнопки управления
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add Row", callback=self.add_table_row)
                dpg.add_button(label="Remove Selected Row", callback=self.remove_table_row)
                dpg.add_button(label="Calculate Selected", callback=self.calculate_selected)
                dpg.add_button(label="Add selected composition to db", callback=self.add_composition_to_db)

    def add_table_row(self):
        global row_counter
        
        # Предопределенные значения
        #compositions = ["Water", "Methane", "Ethane", "CO2", "Nitrogen"]
        compositions = self.compositions_db.get_all_compositions_labels()
        eos_options = ["PR", "SRK", "RK", "VDW"]
        #shift_params = ["0.0", "0.1", "0.2", "0.3", "Custom"]
        shift_params = self.library_db.get_all_shift_labels()
        #acentric_factors = ["0.344", "0.011", "0.225", "0.008", "Custom"]
        acentric_factors = self.library_db.get_all_acentric_factor_labels()
        #critical_pressures = ["73.8 bar", "45.99 bar", "33.94 bar", "Custom"]
        critical_pressures = self.library_db.get_all_pcrit_labels()
        #critical_temps = ["647.1 K", "190.6 K", "305.3 K", "Custom"]
        critical_temps = self.library_db.get_all_tcrit_labels()
        
        with dpg.table_row(parent="main_table", tag=f"row_{self.row_counter}"):
            # Сохраняем данные строки
            row_data = {
                "composition": dpg.add_combo(items=compositions, default_value=compositions[0], width=120, tag=f"comp_{self.row_counter}"),
                "eos": dpg.add_combo(items=eos_options, default_value=eos_options[0], width=80, tag=f"eos_{self.row_counter}"),
                "shift": dpg.add_combo(items=shift_params, default_value=shift_params[0], width=120, tag=f"shift_{self.row_counter}"),
                "acentric": dpg.add_combo(items=acentric_factors, default_value=acentric_factors[0], width=120, tag=f"acentric_{self.row_counter}"),
                "crit_p": dpg.add_combo(items=critical_pressures, default_value=critical_pressures[0], width=120, tag=f"crit_p_{self.row_counter}"),
                "crit_t": dpg.add_combo(items=critical_temps, default_value=critical_temps[0], width=120, tag=f"crit_t_{self.row_counter}"),
                "calculate": dpg.add_checkbox(default_value=True, tag=f"calc_{self.row_counter}")
            }
            
            self.table_data.append(row_data)
            self.row_counter += 1

    def remove_table_row(self):
        if not self.table_data:
            return
        
        # Находим выбранные строки
        selected_rows = []
        for i, row in enumerate(self.table_data):
            if dpg.get_value(f"calc_{i}"):
                selected_rows.append(i)
        
        # Удаляем в обратном порядке, чтобы индексы не сдвигались
        for i in sorted(selected_rows, reverse=True):
            dpg.delete_item(f"row_{i}")
            self.table_data.pop(i)
        
        # Обновляем глобальный счетчик
        global row_counter
        row_counter = len(self.table_data)
        
        # Переиндексируем оставшиеся строки
        for i, row in enumerate(self.table_data):
            for key in row:
                if key != "calculate":  # Чекбоксы не переименовываем
                    new_tag = f"{key.split('_')[0]}_{i}"
                    dpg.configure_item(row[key], tag=new_tag)

    def calculate_selected(self):
        selected_rows = []
        for i, row in enumerate(self.table_data):
            if dpg.get_value(f"calc_{i}"):
                composition = dpg.get_value(f"comp_{i}")
                eos = dpg.get_value(f"eos_{i}")
                shift = dpg.get_value(f"shift_{i}")
                acentric = dpg.get_value(f"acentric_{i}")
                crit_p = dpg.get_value(f"crit_p_{i}")
                crit_t = dpg.get_value(f"crit_t_{i}")
                
                selected_rows.append({
                    "composition": composition,
                    "eos": eos,
                    "shift": shift,
                    "acentric": acentric,
                    "crit_p": crit_p,
                    "crit_t": crit_t
                })
        
        print("Selected for calculation:", selected_rows)

    def add_composition_to_db(self):

        data_to_save = []
        
        for i, row in enumerate(self.table_data):
            composition = dpg.get_value(f"comp_{i}")
            eos = dpg.get_value(f"eos_{i}")
            shift = dpg.get_value(f"shift_{i}")
            acentric = dpg.get_value(f"acentric_{i}")
            crit_p = dpg.get_value(f"crit_p_{i}")
            crit_t = dpg.get_value(f"crit_t_{i}")
            calculate = dpg.get_value(f"calc_{i}")
            
            data_to_save.append({
                "composition": composition,
                "eos": eos,
                "shift_parameter": shift,
                "acentric_factor": acentric,
                "critical_pressure": crit_p,
                "critical_temperature": crit_t,
                "calculate": calculate
            })
        
        print(data_to_save)



class DefineCompositionModelWindow:

    def __init__(self):
        self.compositional_params = {}



    def define_compositional_model_button(self):
        self.compositional_params = {'Label': dpg.get_value('model_label'), 'EOS': dpg.get_value('define_eos_combo'),
                                 'Pcrit': dpg.get_value('define_mm_combo'), 'Tcrit': dpg.get_value('define_tcrit_combo'),
                                   'bips': dpg.get_value('define_bips_combo'), 'shift': dpg.get_value('define_shift_combo')}

        return self.compositional_params



    def create(self):
        with dpg.window(
            label= 'Define compositional model',
            tag= 'define_comp_model',
            no_resize= True,
            no_collapse= True,
            collapsed= True,
            no_close= True,
            width= 600,
            height= 400,
            
        ):
            dpg.add_input_text(label='Model name', tag = 'model_label')
            dpg.add_separator()
            dpg.add_combo( label= 'EOS', tag = 'define_eos_combo',items=['PR', 'RK', 'SRK', 'BrusilovskyEOS'],  default_value= 'PR')
            dpg.add_combo(label='Molar mass data', tag = 'define_mm_combo',
                          items=['basic', 'user'], default_value= 'basic')
            
            dpg.add_combo(label='Pcrit data', tag= 'define_pcrit_combo',
                          items=['basic', 'user'],  default_value= 'basic')
            
            dpg.add_combo(label='Tcrit data', tag = 'define_tcrit_combo',
                          items=['basic', 'user'],  default_value= 'basic')
            
            dpg.add_combo(label='bips data', tag = 'define_bips_combo',
                          items=['basic', 'user'],  default_value= 'basic')
            
            dpg.add_checkbox(label='Use shift parametr')

            dpg.add_combo(label='Shift data', tag = 'define_shift_combo',
                          items=['basic', 'user'],  default_value= 'basic')
            
            dpg.add_button(label='Define compositional model')

#Этот класс кажется что не нужен. Его функционал перенесен в Compositions
class CompositionWindow:
    def __init__(self, flash_calc: FlashCalculator):
        self.flash_calc = flash_calc
        
    def create(self):
        pos = WINDOW_POSITIONS["composition_window"]
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
                            callback=lambda s, a, u: self.flash_calc.update_composition(u, a),
                            user_data=component
                        )

class FlashInputWindow:
    def __init__(self, flash_calc: FlashCalculator, results_callback):
        self.flash_calc = flash_calc
        self.results_callback = results_callback
        
    def create(self):
        pos = WINDOW_POSITIONS['flash_input_window']
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
                callback=lambda s, a: self.flash_calc.update_pt(a, self.flash_calc.temperature)
            )
            dpg.add_input_float(
                label='Temperature, °C',
                tag='input_temperature',
                callback=lambda s, a: self.flash_calc.update_pt(self.flash_calc.pressure, a)
            )
            dpg.add_button(
                label='Calculate Flash',
                callback=self.results_callback
            )

class FlashOutputWindow:
    def __init__(self, flash_calc: FlashCalculator):
        self.flash_calc = flash_calc
        
    def create(self):
        pos = WINDOW_POSITIONS['results_window']
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
            results = self.flash_calc.calculate_flash()
            dpg.add_input_text(
                multiline=True,
                height=280,
                width=380,
                default_value=results,
                readonly=True,
                tag='flash_results_output'
            )

def show_compositional_interface(flash_calc: FlashCalculator):
    # define_model_window = DefineCompositionModelWindow()
    # define_model_window.create()

    comp2 = Compositions()
    comp2.create()

    variants = CompositionVariants()
    variants.create_composition_variants_window()


    #comp_window = CompositionWindow(flash_calc)
    #flash_input = FlashInputWindow(flash_calc, lambda: show_results(flash_calc))

    #comp_window.create()
    #flash_input.create()

def show_results(flash_calc: FlashCalculator):
    ...
    if dpg.does_item_exist('results_window'):
        dpg.delete_item('results_window')
    output_window = FlashOutputWindow(flash_calc)
    output_window.create()

def show_define_model_interface():
    ...
    compositions = Compositions()
    compositions.show_composition_management_window()
    define_model_window = DefineCompositionModelWindow()
    define_model_window.create()