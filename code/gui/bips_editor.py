# bips_editor.py
import dearpygui.dearpygui as dpg

class BIPSEditor:
    """Редактор бинарных параметров взаимодействия (BIPS)"""
    
    def __init__(self):
        self.default_bips = {
            ("C1", "CO2"): 0.1,
            ("C1", "N2"): 0.02,
            ("CO2", "H2S"): 0.12,
            # Можно добавить больше дефолтных значений
        }
    
    def setup_editor(self, parent):
        """Настройка редактора BIPS"""
        with dpg.group(parent=parent):
            dpg.add_text("Binary Interaction Parameters (BIPS)", color=(0, 200, 255))
            dpg.add_text("Configure interaction parameters between components", color=(200, 200, 0))
            
            self._setup_bips_matrix()
            dpg.add_separator()
            self._setup_bips_controls()
    
    def _setup_bips_matrix(self):
        """Настройка матрицы BIPS"""
        with dpg.group():
            dpg.add_text("BIP Matrix:")
            
            sample_components = ["C1", "C2", "C3", "nC4", "nC5", "C6", "C7+", "CO2", "N2"]
            
            with dpg.table(
                header_row=True, 
                borders_innerH=True, 
                borders_outerH=True,
                height=300,
                width=-1
            ):
                dpg.add_table_column(label="Component")
                
                for comp in sample_components:
                    dpg.add_table_column(label=comp)
                
                for i, comp1 in enumerate(sample_components):
                    with dpg.table_row():
                        dpg.add_text(comp1)
                        for j, comp2 in enumerate(sample_components):
                            if i == j:
                                dpg.add_text("0.000")
                            else:
                                default_value = self.default_bips.get((comp1, comp2), 0.0)
                                dpg.add_input_float(
                                    default_value=default_value,
                                    step=0.001,
                                    format="%.3f",
                                    width=60,
                                    tag=f"bip_{comp1}_{comp2}"
                                )
    
    def _setup_bips_controls(self):
        """Настройка элементов управления BIPS"""
        with dpg.group(horizontal=True):
            dpg.add_button(label="Reset to Defaults", callback=self.reset_to_defaults, width=120)
            dpg.add_button(label="Calculate Optimal BIPS", width=150)
            dpg.add_button(label="Import BIPS Matrix", width=120)
    
    def reset_to_defaults(self):
        """Сброс к значениям по умолчанию"""
        sample_components = ["C1", "C2", "C3", "nC4", "nC5", "C6", "C7+", "CO2", "N2"]
        
        for i, comp1 in enumerate(sample_components):
            for j, comp2 in enumerate(sample_components):
                if i != j:
                    tag = f"bip_{comp1}_{comp2}"
                    if dpg.does_item_exist(tag):
                        default_value = self.default_bips.get((comp1, comp2), 0.0)
                        dpg.set_value(tag, default_value)
    
    def get_bips_matrix(self) -> dict:
        """Получение матрицы BIPS"""
        bips = {}
        sample_components = ["C1", "C2", "C3", "nC4", "nC5", "C6", "C7+", "CO2", "N2"]
        
        for i, comp1 in enumerate(sample_components):
            for j, comp2 in enumerate(sample_components):
                if i != j:
                    tag = f"bip_{comp1}_{comp2}"
                    if dpg.does_item_exist(tag):
                        bips[(comp1, comp2)] = dpg.get_value(tag)
        
        return bips