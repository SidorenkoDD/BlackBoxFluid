# fluid_database.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

class FluidDatabase:
    """Управление базой данных флюидов"""
    
    def __init__(self, db_path: str = "fluids_database.json"):
        self.db_path = db_path
        self.fluids: List[Dict[str, Any]] = []
        self.current_fluid: Optional[Dict[str, Any]] = None
        self.load_fluids()
    
    def load_fluids(self):
        """Загрузка флюидов из файла базы данных"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    self.fluids = json.load(f)
            else:
                # Инициализация демо-данными
                self.fluids = [
                    {
                        "name": "North Sea Oil", 
                        "type": "Black Oil", 
                        "components": 8, 
                        "mw": 125.4, 
                        "date": "2024-01-15"
                    },
                    {
                        "name": "Gas Condensate", 
                        "type": "Gas Condensate", 
                        "components": 12, 
                        "mw": 89.2, 
                        "date": "2024-01-10"
                    },
                    {
                        "name": "Dry Gas Field", 
                        "type": "Dry Gas", 
                        "components": 6, 
                        "mw": 19.8, 
                        "date": "2024-01-05"
                    }
                ]
                self.save_fluids()
        except Exception as e:
            print(f"Error loading fluids database: {e}")
            self.fluids = []
    
    def save_fluids(self):
        """Сохранение флюидов в файл"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.fluids, f, indent=2)
        except Exception as e:
            print(f"Error saving fluids database: {e}")
    
    def add_fluid(self, fluid_data: Dict[str, Any]):
        """Добавление нового флюида"""
        fluid_data["date"] = datetime.now().strftime("%Y-%m-%d")
        self.fluids.append(fluid_data)
        self.save_fluids()
    
    def delete_fluid(self, index: int):
        """Удаление флюида по индексу"""
        if 0 <= index < len(self.fluids):
            del self.fluids[index]
            self.save_fluids()
    
    def copy_fluid(self, index: int) -> Dict[str, Any]:
        """Копирование флюида"""
        if 0 <= index < len(self.fluids):
            original = self.fluids[index].copy()
            original["name"] = f"{original['name']}_Copy"
            original["date"] = datetime.now().strftime("%Y-%m-%d")
            return original
        return {}
    
    def get_fluid_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Получение флюида по индексу"""
        if 0 <= index < len(self.fluids):
            return self.fluids[index]
        return None
    
    def find_fluid_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Поиск флюида по имени"""
        for fluid in self.fluids:
            if fluid["name"] == name:
                return fluid
        return None