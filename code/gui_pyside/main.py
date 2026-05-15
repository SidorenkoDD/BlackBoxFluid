# main.py
import sys
from pathlib import Path

# Добавляем пути к вашему ядру
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from PySide6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("CompositionalFluid")
    app.setApplicationName("FluidModeling")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()