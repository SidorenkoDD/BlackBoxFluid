# db_reader.py
import yaml
from pathlib import Path

class DBReader:
    def __init__(self, db_path="code/db.yaml"):
        self.db_path = Path(db_path)
        
    def get_keys(self):
        if not self.db_path.exists():
            return []
            
        with self.db_path.open('r') as f:
            data = yaml.safe_load(f) or {}
        return list(data.keys())
    
    def get_data(self, key: str):
        if not self.db_path.exists():
            return {}
            
        with self.db_path.open('r') as f:
            data = yaml.safe_load(f) or {}
        return data.get(key, {})