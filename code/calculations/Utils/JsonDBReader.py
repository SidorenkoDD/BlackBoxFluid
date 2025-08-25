import json
import os
from pathlib import Path
from calculations.Utils.BaseClasses import Reader

class JsonDBReader(Reader):
    def _find_db_file(self):
        """Поиск DB.json в различных возможных местах"""
        # Получаем директорию, где находится этот скрипт
        script_dir = Path(__file__).parent
        
        possible_paths = [
            # Относительно расположения этого скрипта
            script_dir / 'DB.json',
            # На уровень выше (если скрипт в папке Utils)
            script_dir.parent / 'DB.json',
            # Текущая рабочая директория
            Path.cwd() / 'DB.json',
            # Из переменной окружения
            Path(os.getenv('DB_PATH')) if os.getenv('DB_PATH') else None,
        ]
        
        # Убираем None значения
        possible_paths = [path for path in possible_paths if path is not None]
        
        for path in possible_paths:
            if path.exists():
                return path

        
        raise FileNotFoundError("DB.json not found in any expected location")


    def load_database(self):
        """Загрузка базы данных"""
        db_path = self._find_db_file()
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
