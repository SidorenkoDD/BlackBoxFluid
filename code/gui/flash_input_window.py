import dearpygui.dearpygui as dpg
from models.flash_calculator import FlashCalculator

class FlashInputWindow:
    def __init__(self, calculator: FlashCalculator, position: dict, calculate_callback: callable):
        self.calculator = calculator
        self.position = position
        self.calculate_callback = calculate_callback
        self.tag = "flash_input_window"

    def create(self) -> None:
        """Создаёт окно для ввода параметров P и T."""
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
            
        with dpg.window(
            label='Flash Input Parameters',
            tag=self.tag,
            width=self.position['width'],
            height=self.position['height'],
            pos=(self.position['x'], self.position['y']),
            no_resize=False,
            no_collapse=False,
            no_close=True
        ):
            dpg.add_input_float(
                label='Pressure, bar',
                tag='input_pressure',
                default_value=0.0,
                min_value=0.0,
                min_clamped=True,
                step=0.1,
                callback=lambda s, a: self.calculator.update_pt(a, self.calculator.temperature)
            )
            dpg.add_input_float(
                label='Temperature, °C',
                tag='input_temperature',
                default_value=0.0,
                min_value=-273.15,
                min_clamped=True,
                step=1.0,
                callback=lambda s, a: self.calculator.update_pt(self.calculator.pressure, a)
            )
            dpg.add_button(
                label='Calculate Flash',
                callback=self.calculate_callback
            )