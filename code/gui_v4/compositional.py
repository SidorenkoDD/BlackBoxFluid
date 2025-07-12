# compositional.py
import dearpygui.dearpygui as dpg
from flash_calculator import FlashCalculator
from constants import COMPONENTS, WINDOW_POSITIONS
from CompositionsJSONReader import CompositionsJSONReader


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


    # comp_window = CompositionWindow(flash_calc)
    # flash_input = FlashInputWindow(flash_calc, lambda: show_results(flash_calc))

    # comp_window.create()
    # flash_input.create()

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