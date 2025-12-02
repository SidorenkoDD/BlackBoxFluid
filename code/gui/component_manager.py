# component_manager.py
from typing import List, Dict, Set

class ComponentManager:
    """Управление компонентами флюидов"""
    
    def __init__(self):
        self.all_components = self._get_all_components()
        self.next_row_index = 0
        self.hydrocarbon_components = self._get_hydrocarbon_components()
    
    def _get_all_components(self) -> List[str]:
        """Получение всех доступных компонентов"""
        base_components = ["C1", "C2", "C3", "iC4", "nC4", "iC5", "nC5", "C6", "C7+"]
        non_hydrocarbons = ["N2", "CO2", "H2S", "H2", "O2", "CO", "H2O"]
        heavy_components = [
            "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15",
            "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25",
            "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35",
            "C36", "C37", "C38", "C39", "C40"
        ]
        
        return base_components + non_hydrocarbons + heavy_components
    
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
    
    def get_component_categories(self) -> Dict[str, List[str]]:
        """Получение компонентов по категориям"""
        return {
            "Light Hydrocarbons": ["C1", "C2", "C3", "iC4", "nC4", "iC5", "nC5"],
            "Heavy Hydrocarbons": [comp for comp in self.all_components if comp.startswith("C") and comp not in ["C1", "C2", "C3", "iC4", "nC4", "iC5", "nC5", "C6", "C7+"]],
            "Non-Hydrocarbons": ["N2", "CO2", "H2S", "H2", "O2", "CO", "H2O"],
            "Plus Fractions": ["C7+"]
        }
    
    def validate_component_name(self, name: str) -> bool:
        """Проверка валидности имени компонента"""
        return name in set(self.all_components)
    
    def get_next_row_id(self) -> int:
        """Получение следующего ID для строки"""
        self.next_row_index += 1
        return self.next_row_index - 1