# widgets.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QDockWidget, QMainWindow, QLabel, QSplitter, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog
)
from PySide6.QtGui import QFont, QColor


class PropertiesTableWidget(QWidget):
    """Таблица для отображения и редактирования свойств компонентов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.core_bridge = None
        
        layout = QVBoxLayout(self)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Компонент", "Мольная доля", "M (г/моль)", 
            "Tc (K)", "Pc (МПа)", "ω", "Vc (см³/моль)"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        
        layout.addWidget(self.table)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_data)
        edit_btn = QPushButton("✏️ Редактировать")
        edit_btn.clicked.connect(self.edit_selected)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(edit_btn)
        layout.addLayout(btn_layout)
    
    def set_composition(self, core_bridge):
        """Установка моста с ядром"""
        self.core_bridge = core_bridge
        self.refresh_data()
    
    def refresh_data(self):
        """Обновление данных в таблице"""
        if not self.core_bridge or not self.core_bridge.has_composition():
            return
        
        properties = self.core_bridge.get_all_components_properties()
        
        self.table.setRowCount(len(properties))
        for row, (comp, props) in enumerate(properties.items()):
            self.table.setItem(row, 0, QTableWidgetItem(comp))
            self.table.setItem(row, 1, QTableWidgetItem(f"{props.get('mole_fraction', 0):.6f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{props.get('molar_mass', 0):.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{props.get('critical_temperature', 0):.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{props.get('critical_pressure', 0)/1e6:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{props.get('acentric_factor', 0):.4f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{props.get('critical_volume', 0):.2f}"))
        
        self.table.resizeColumnsToContents()
    
    def edit_selected(self):
        """Редактирование выбранного компонента"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите компонент для редактирования")
            return
        
        component = self.table.item(current_row, 0).text()
        
        # Диалог редактирования
        from PySide6.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование свойств: {component}")
        layout = QFormLayout(dialog)
        
        # Поля для редактирования
        current_props = self.core_bridge.get_component_properties(component)
        
        fields = {}
        for prop, label in [
            ('molar_mass', 'Молярная масса (г/моль)'),
            ('critical_temperature', 'Критическая температура (K)'),
            ('critical_pressure', 'Критическое давление (МПа)'),
            ('acentric_factor', 'Ацентрический фактор'),
            ('critical_volume', 'Критический объем (см³/моль)')
        ]:
            spin = QDoubleSpinBox()
            spin.setRange(-1e9, 1e9)
            spin.setDecimals(4)
            spin.setValue(current_props.get(prop, 0))
            if prop == 'critical_pressure':
                spin.setValue(spin.value() / 1e6)
            layout.addRow(label, spin)
            fields[prop] = spin
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            for prop, spin in fields.items():
                value = spin.value()
                if prop == 'critical_pressure':
                    value *= 1e6
                try:
                    self.core_bridge.update_component_property(component, prop, value)
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", str(e))
            
            self.refresh_data()


class ResultWindow(QMainWindow):
    """Отдельное окно для результатов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результаты расчета")
        self.resize(600, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.save_result)
        layout.addWidget(save_btn)
    
    def set_content(self, content):
        self.text_edit.setPlainText(str(content))
    
    def save_result(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результат", "result.txt", "Text files (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())


class DockableResultWindow(QDockWidget):
    """Док-панель для результатов"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        
        widget = QWidget()
        self.setWidget(widget)
        layout = QVBoxLayout(widget)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.save_content)
        clear_btn = QPushButton("🗑 Очистить")
        clear_btn.clicked.connect(self.clear_content)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
    
    def set_content(self, content):
        self.text_edit.setPlainText(str(content))
    
    def append_content(self, content):
        self.text_edit.append(str(content))
    
    def clear_content(self):
        self.text_edit.clear()
    
    def save_content(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результат", "result.txt", "Text files (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())