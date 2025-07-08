from pathlib import Path
from typing import Dict, List, Any

# Константы для позиционирования окон
WINDOW_POSITIONS: Dict[str, Dict[str, int]] = {
    "composition_window": {"x": 10, "y": 30, "width": 400, "height": 300},
    "flash_input_window": {"x": 420, "y": 30, "width": 400, "height": 300},
    "results_window": {"x": 420, "y": 340, "width": 400, "height": 300}
}

# Компоненты системы
COMPONENTS: List[str] = ['C1', 'C2', 'C3', 'nC4', 'iC4', 'nC5', 'iC5']

# Пути к файлам
DB_PATH: Path = Path("code/db.yaml")