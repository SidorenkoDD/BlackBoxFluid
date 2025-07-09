# compositional.py
import dearpygui.dearpygui as dpg
from flash_calculator import FlashCalculator
from constants import COMPONENTS, WINDOW_POSITIONS

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
    comp_window = CompositionWindow(flash_calc)
    flash_input = FlashInputWindow(flash_calc, lambda: show_results(flash_calc))
    comp_window.create()
    flash_input.create()

def show_results(flash_calc: FlashCalculator):
    if dpg.does_item_exist('results_window'):
        dpg.delete_item('results_window')
    output_window = FlashOutputWindow(flash_calc)
    output_window.create()