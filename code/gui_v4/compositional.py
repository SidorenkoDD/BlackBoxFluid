# compositional.py
import dearpygui.dearpygui as dpg
from flash_calculator import FlashCalculator
from constants import COMPONENTS, WINDOW_POSITIONS
from CompositionsJSONReader import CompositionsJSONReader

class Compositions:
    def __init__(self):
        pass

    def add_composition_callback(self):
        print("Add Composition clicked")
        # Здесь можно добавить логику для добавления новой композиции
        
    def edit_composition_callback(self):
        print("Edit Composition clicked")
        # Здесь можно добавить логику для редактирования композиции
        
    def delete_composition_callback(self):
        print("Delete Composition clicked")
        # Здесь можно добавить логику для удаления композиции

    def create(self):
        with dpg.window(label="Compositions Manager", width=400, height=400):
            dpg.add_text("Compositions Manager")
            dpg.add_separator()
            
            # Кнопка добавления композиции
            dpg.add_button(label="Add Composition", 
                        callback=self.show_add_composition_modal,
                        width=150, height=30)
            
            # Кнопка редактирования композиции
            dpg.add_button(label="Edit Composition", 
                        callback=self.edit_composition_callback,
                        width=150, height=30)
            
            # Кнопка удаления композиции
            dpg.add_button(label="Delete Composition", 
                        callback=self.delete_composition_callback,
                        width=150, height=30)
            
            dpg.add_separator()
            dpg.add_text('Avalible compositions')

            self.comp_reader = CompositionsJSONReader()


            dpg.add_combo(list(self.comp_reader.get_all_compositions_labels()), tag='compositions_combo',
                           default_value=list(self.comp_reader.get_all_compositions_labels())[0])
    
            dpg.add_text('Model Info:')
            dpg.add_text(str(self.comp_reader.get_composition_info(dpg.get_value('compositions_combo'))))
            dpg.add_text('Model Composition:')
            dpg.add_text(str(self.comp_reader.get_composition(dpg.get_value('compositions_combo'))))


    

    def save_new_composition(self, sender, app_data):
        # Получаем имя композиции из input текста
        composition_name = dpg.get_value("new_composition_name")  # предполагается, что у input_text есть tag "Name"
        
        # Собираем все компоненты и их значения из таблицы
        composition = {}
        for component in COMPONENTS:
            input_tag = f"input_{component}"
            value = dpg.get_value(input_tag)
            composition[component] = value
        
        # Здесь можно добавить логику сохранения композиции
        print(f"Saving composition '{composition_name}': {composition}")
        
        # Закрываем модальное окно
        #dpg.delete_item(dpg.last_container())

    def save_new_composition_v2(self):
    # Получаем имя композиции
        composition_name = dpg.get_value("new_composition_name")
        
        if not composition_name:
            print("Error: Composition name cannot be empty!")
            return
        
        # Собираем компоненты и их значения
        composition = {}
        for component in COMPONENTS:
            input_tag = f"input_{component}"
            try:
                value = dpg.get_value(input_tag)
                if value is not None:  # Проверяем, что значение было установлено
                    composition[component] = value
            except Exception as e:
                print(f"Error getting value for component {component}: {e}")
        
        # Проверяем, что хотя бы один компонент имеет ненулевое значение
        if not any(composition.values()):
            print("Error: At least one component must have non-zero value!")
            return
        
        # Здесь должна быть логика сохранения композиции
        print(f"Saving composition '{composition_name}': {composition}")
        
        # Пример добавления в JSON reader (если у вас есть такой функционал)
        if hasattr(self, 'comp_reader'):
            self.comp_reader.add_composition(composition_name=composition_name, composition=composition)
        
        # Обновляем список композиций в основном окне
        if dpg.does_item_exist('compositions_combo'):
            dpg.configure_item('compositions_combo', items=list(self.comp_reader.get_all_compositions_labels()))
        
        # Закрываем модальное окно
        dpg.delete_item(dpg.get_active_window())


    def show_add_composition_modal(self):
        if dpg.does_item_exist("add_composition_modal"):
            dpg.delete_item("add_composition_modal")

        with dpg.window(label="Add New Composition", no_close=False,  modal=True, width=400, height=700, tag = 'add_composition_modal'):
            dpg.add_text("Enter composition:")
            dpg.add_input_text(label="Name", tag = 'new_composition_name')
            dpg.add_button(label="Save", callback= self.save_new_composition_v2) 
            dpg.add_button(label="Cancel") #callback=lambda: dpg.delete_item(dpg.last_container()))
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


    #comp_window = CompositionWindow(flash_calc)
    #flash_input = FlashInputWindow(flash_calc, lambda: show_results(flash_calc))

    #comp_window.create()
    #flash_input.create()

def show_results(flash_calc: FlashCalculator):
    ...
    # if dpg.does_item_exist('results_window'):
    #     dpg.delete_item('results_window')
    # output_window = FlashOutputWindow(flash_calc)
    # output_window.create()

def show_define_model_interface():
    ...
    #compositions = Compositions()
    #compositions.show_composition_management_window()
    # define_model_window = DefineCompositionModelWindow()
    # define_model_window.create()