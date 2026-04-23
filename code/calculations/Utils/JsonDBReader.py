import json
import os
import sys
from pathlib import Path
from calculations.Utils.BaseClasses import Reader


class JsonDBReader(Reader):
    def _find_db_file(self, db_filename):
        """Поиск DB.json с учетом различных сценариев запуска"""
        current_file_path = Path(__file__).absolute()
        
        possible_paths = [
            # Рядом с текущим файлом
            current_file_path.parent / db_filename,
            # В корне проекта (предполагаем, что текущий файл в подпапке)
            current_file_path.parent.parent / db_filename,
            # В рабочей директории
            Path.cwd() / db_filename,
            # Рядом с исполняемым скриптом
            Path(sys.argv[0]).parent / db_filename,
            # Из переменной окружения
            Path(os.getenv('DB_PATH')) if os.getenv('DB_PATH') else None,
        ]
        
        # Добавляем поиск вверх по иерархии директорий
        for level in range(1, 5):  # Проверяем до 4 уровней вверх
            parent_dir = current_file_path.parents[level]
            possible_paths.append(parent_dir / db_filename)
        
        # Убираем None и дубликаты
        possible_paths = [path for path in possible_paths if path is not None]
        possible_paths = list(dict.fromkeys(possible_paths))  # Remove duplicates
        
        for path in possible_paths:
            if path.exists():
                #print(f"Found DB.json at: {path}")
                return path
        
        
        raise FileNotFoundError(f"{db_filename} not found in any expected location")
    
    def load_database(self, db_filename: str = 'DB.json'):
        db_path = self._find_db_file(db_filename)
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
