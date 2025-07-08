import dearpygui.dearpygui as dpg
from typing import List
from models.flash_calculator import FlashCalculator

class CompositionWindow:
    def __init__(self, calculator: FlashCalculator, position: dict, components: List[str]):
        self.calculator = calculator
        self.position = position
        self.components = components
        self.tag = "composition_window"
    
    def create(self) -> None:
        """Создаёт окно для ввода состава."""
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)

        with dpg.window(
            label='Composition Input',
            tag=self.tag,
            width=self.position['width'],
            height=self.position['height'],
            pos=(self.position['x'], self.position['y']),
            no_resize=False,
            no_collapse=False,
            no_close=True
        ):
            self._create_composition_table()
    
    def _create_composition_table(self) -> None:
        """Создаёт таблицу состава."""
        with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit):
            dpg.add_table_column(label='Component')
            dpg.add_table_column(label='Mole Fraction')
            
            for component in self.components:
                with dpg.table_row():
                    dpg.add_text(component)
                    dpg.add_input_float(
                        default_value=0.0,
                        tag=f"input_{component}",
                        step=0.05,
                        min_value=0.0,
                        max_value=1.0,
                        min_clamped=True,
                        max_clamped=True,
                        callback=lambda s, a, u: self.calculator.update_composition(u, a),
                        user_data=component
                    )