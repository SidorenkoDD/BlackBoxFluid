# fluid_properties_editor.py
import dearpygui.dearpygui as dpg

class FluidPropertiesEditor:
    """Редактор свойств и корреляций флюида"""
    
    def __init__(self):
        self.correlation_methods = {
            "critical_temperature": ["Twu (1984)", "Soave (1972)", "Peng-Robinson (1976)", "Custom"],
            "critical_pressure": ["Twu (1984)", "Soave (1972)", "Peng-Robinson (1976)", "Custom"],
            "acentric_factor": ["Lee-Kesler (1975)", "Edmister (1958)", "Custom"],
            "molecular_weight": ["Katz-Firoozabadi (1978)", "Kesler-Lee (1976)", "Custom"],
            "vapor_pressure": ["Lee-Kesler (1975)", "Antoine", "Custom"]
        }
    
    def setup_editor(self, parent):
        """Настройка редактора свойств"""
        with dpg.group(parent=parent):
            dpg.add_text("Properties & Correlations", color=(0, 200, 255))
            dpg.add_text("Component Properties Configuration", color=(200, 200, 0))
            
            self._setup_correlation_methods()
            dpg.add_separator()
            self._setup_mixing_rules()
    
    def _setup_correlation_methods(self):
        """Настройка методов корреляции"""
        with dpg.group():
            dpg.add_text("Critical properties correlation methods:")
            with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True):
                dpg.add_table_column(label="Property")
                dpg.add_table_column(label="Correlation Method")
                
                properties = [
                    ("Critical Temperature", "critical_temperature"),
                    ("Critical Pressure", "critical_pressure"), 
                    ("Acentric Factor", "acentric_factor"),
                    ("Molecular Weight", "molecular_weight"),
                    ("Vapor Pressure", "vapor_pressure")
                ]
                
                for prop_name, prop_key in properties:
                    with dpg.table_row():
                        dpg.add_text(prop_name)
                        dpg.add_combo(
                            items=self.correlation_methods[prop_key],
                            default_value=self.correlation_methods[prop_key][0],
                            width=200,
                            tag=f"correlation_{prop_key}"
                        )
    
    def _setup_mixing_rules(self):
        """Настройка правил смешивания"""
        dpg.add_text("Mixing Rules", color=(200, 200, 0))
        dpg.add_radio_button(
            items=["Van der Waals", "Modified Huron-Vidal", "Wong-Sandler"],
            default_value="Van der Waals",
            tag="mixing_rules"
        )
    
    def get_correlation_methods(self) -> dict:
        """Получение выбранных методов корреляции"""
        methods = {}
        for prop_key in self.correlation_methods.keys():
            tag = f"correlation_{prop_key}"
            if dpg.does_item_exist(tag):
                methods[prop_key] = dpg.get_value(tag)
        return methods
    
    def get_mixing_rule(self) -> str:
        """Получение выбранного правила смешивания"""
        return dpg.get_value("mixing_rules") if dpg.does_item_exist("mixing_rules") else "Van der Waals"