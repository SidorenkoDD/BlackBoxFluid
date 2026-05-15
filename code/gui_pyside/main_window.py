# main_window.py
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import (
    QMainWindow, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QDockWidget, QToolBar, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QFileDialog, QTabWidget, QWidget, QVBoxLayout,
    QPushButton, QSplitter, QInputDialog, QDialog, QDialogButtonBox,
    QComboBox, QLabel, QDoubleSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtGui import QAction, QFont, QIcon
import json
from typing import Dict, Any, Optional

from widgets import ResultWindow, DockableResultWindow, PropertiesTableWidget
from core_bridge import CoreBridge


class CorrelationsDialog(QDialog):
    """Диалог выбора корреляций для критических свойств"""
    
    def __init__(self, parent=None, available_correlations=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор корреляций критических свойств")
        self.setModal(True)
        self.available_correlations = available_correlations or {}
        self.selected_correlations = {}
        
        layout = QVBoxLayout(self)
        
        # Создаем группу для каждого типа свойства
        for prop_name, correlations in self.available_correlations.items():
            group = QGroupBox(prop_name.replace('_', ' ').title())
            group_layout = QVBoxLayout()
            
            combo = QComboBox()
            combo.addItems(correlations)
            combo.setCurrentText(correlations[0])
            self.selected_correlations[prop_name] = combo
            
            group_layout.addWidget(combo)
            group.setLayout(group_layout)
            layout.addWidget(group)
        
        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_selected_correlations(self):
        return {prop: combo.currentText() for prop, combo in self.selected_correlations.items()}


class EOSDialog(QDialog):
    """Диалог выбора уравнения состояния"""
    
    def __init__(self, parent=None, available_eos=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор уравнения состояния")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.eos_combo = QComboBox()
        self.eos_combo.addItems(available_eos or ['Peng-Robinson', 'SRK', 'PRSV'])
        
        layout.addWidget(QLabel("Уравнение состояния:"))
        layout.addWidget(self.eos_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_selected_eos(self):
        return self.eos_combo.currentText()


class MainWindow(QMainWindow):
    SETTINGS_GROUP = "main_window"
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.core_bridge = CoreBridge()
        self.result_windows = {}
        self.dock_windows = {}
        
        self.setWindowTitle("Compositional Fluid Modeling")
        self.resize(1400, 900)
        
        self._setup_ui()
        self._connect_signals()
        self._restore_layout()
    
    def _setup_ui(self):
        """Инициализация всего UI"""
        self._build_central()
        self._build_docks()
        self._build_actions()
        self._build_menu()
        self._build_toolbar()
        self._build_statusbar()
    
    def _build_central(self):
        """Создание центральной области"""
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabsClosable(True)
        self.central_tabs.tabCloseRequested.connect(self._close_central_tab)
        
        # Приветственная вкладка
        welcome_widget = self._create_welcome_widget()
        self.central_tabs.addTab(welcome_widget, "Главная")
        self.setCentralWidget(self.central_tabs)
    
    def _create_welcome_widget(self):
        """Создание приветственного виджета"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        welcome_text = QTextEdit()
        welcome_text.setReadOnly(True)
        welcome_text.setPlainText(
            "Композиционное моделирование флюида\n\n"
            "Рабочий процесс:\n"
            "1. Файл → Импорт состава XLSX\n"
            "2. Расчет → Корреляции критических свойств\n"
            "3. Расчет → Выбрать уравнение состояния\n"
            "4. Расчет → Flash расчет / Давление насыщения\n\n"
            "💡 Совет: Открывайте результаты в отдельных окнах или док-панелях,\n"
            "   чтобы настроить интерфейс под себя."
        )
        
        # Быстрые кнопки
        quick_buttons = QWidget()
        btn_layout = QVBoxLayout(quick_buttons)
        
        import_btn = QPushButton("📂 Импортировать состав")
        import_btn.clicked.connect(self.on_import_xlsx)
        btn_layout.addWidget(import_btn)
        
        layout.addWidget(welcome_text)
        layout.addWidget(quick_buttons)
        
        return widget
    
    def _build_docks(self):
        """Создание док-панелей"""
        # Дерево проекта
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderHidden(True)
        self._fill_project_tree()
        self.project_tree.itemDoubleClicked.connect(self._on_project_item_double_clicked)
        
        self.project_dock = QDockWidget("📁 Проект", self)
        self.project_dock.setWidget(self.project_tree)
        self.project_dock.setObjectName("project_dock")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_dock)
        
        # Лог
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlainText("Лог приложения\n" + "="*50 + "\n")
        self.log_dock = QDockWidget("📝 Лог", self)
        self.log_dock.setWidget(self.log_view)
        self.log_dock.setObjectName("log_dock")
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        
        # Таблица свойств (будет отображаться когда загружен состав)
        self.properties_table = PropertiesTableWidget()
        self.properties_dock = QDockWidget("📊 Свойства компонентов", self)
        self.properties_dock.setWidget(self.properties_table)
        self.properties_dock.setObjectName("properties_dock")
        self.properties_dock.hide()
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)
    
    def _fill_project_tree(self):
        """Заполнение дерева проекта"""
        self.project_tree.clear()
        
        root = QTreeWidgetItem(["Проект"])
        
        # Входные данные
        input_group = QTreeWidgetItem(["📥 Входные данные"])
        self.composition_item = QTreeWidgetItem(["Состав: не загружен"])
        input_group.addChild(self.composition_item)
        self.properties_item = QTreeWidgetItem(["Критические свойства: не рассчитаны"])
        input_group.addChild(self.properties_item)
        
        # Модель
        model_group = QTreeWidgetItem(["⚙️ Модель"])
        self.eos_item = QTreeWidgetItem(["Уравнение состояния: не выбрано"])
        model_group.addChild(self.eos_item)
        self.correlations_item = QTreeWidgetItem(["Корреляции: не выбраны"])
        model_group.addChild(self.correlations_item)
        
        # Результаты
        results_group = QTreeWidgetItem(["📈 Результаты"])
        self.flash_item = QTreeWidgetItem(["Flash расчет: не выполнялся"])
        self.pb_item = QTreeWidgetItem(["Давление насыщения: не рассчитывалось"])
        results_group.addChildren([self.flash_item, self.pb_item])
        
        root.addChildren([input_group, model_group, results_group])
        self.project_tree.addTopLevelItem(root)
        self.project_tree.expandAll()
    
    def _build_actions(self):
        """Создание действий"""
        # Файл
        self.act_import_xlsx = QAction("📂 Импорт состава XLSX", self)
        self.act_import_xlsx.triggered.connect(self.on_import_xlsx)
        
        self.act_exit = QAction("Выход", self)
        self.act_exit.triggered.connect(self.close)
        
        # Расчет
        self.act_select_correlations = QAction("📐 Корреляции критических свойств", self)
        self.act_select_correlations.triggered.connect(self.on_select_correlations)
        
        self.act_select_eos = QAction("⚙️ Выбрать уравнение состояния", self)
        self.act_select_eos.triggered.connect(self.on_select_eos)
        
        self.act_flash = QAction("💧 Flash расчет", self)
        self.act_flash.triggered.connect(self.on_flash_calc)
        
        self.act_pb = QAction("📊 Давление насыщения", self)
        self.act_pb.triggered.connect(self.on_pb_calc)
        
        # Окна
        self.act_new_result_window = QAction("🪟 Новое окно результатов", self)
        self.act_new_result_window.triggered.connect(self._create_result_window)
        
        self.act_new_dock_result = QAction("📌 Новая док-панель результатов", self)
        self.act_new_dock_result.triggered.connect(self._create_result_dock)
        
        self.act_show_project = QAction("Показать проект", self, checkable=True, checked=True)
        self.act_show_project.toggled.connect(self.project_dock.setVisible)
        
        self.act_show_log = QAction("Показать лог", self, checkable=True, checked=True)
        self.act_show_log.toggled.connect(self.log_dock.setVisible)
        
        self.act_show_properties = QAction("Показать свойства", self, checkable=True, checked=False)
        self.act_show_properties.toggled.connect(self.properties_dock.setVisible)
        
        # Справка
        self.act_about = QAction("О программе", self)
        self.act_about.triggered.connect(self._about)
    
    def _build_menu(self):
        """Создание меню"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # Файл
        file_menu = QMenu("Файл", self)
        file_menu.addAction(self.act_import_xlsx)
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)
        
        # Расчет
        calc_menu = QMenu("Расчет", self)
        calc_menu.addAction(self.act_select_correlations)
        calc_menu.addAction(self.act_select_eos)
        calc_menu.addSeparator()
        calc_menu.addAction(self.act_flash)
        calc_menu.addAction(self.act_pb)
        
        # Окна
        windows_menu = QMenu("Окна", self)
        windows_menu.addAction(self.act_new_result_window)
        windows_menu.addAction(self.act_new_dock_result)
        windows_menu.addSeparator()
        windows_menu.addAction(self.act_show_project)
        windows_menu.addAction(self.act_show_log)
        windows_menu.addAction(self.act_show_properties)
        
        # Справка
        help_menu = QMenu("Справка", self)
        help_menu.addAction(self.act_about)
        
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(calc_menu)
        menu_bar.addMenu(windows_menu)
        menu_bar.addMenu(help_menu)
    
    def _build_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Основное", self)
        toolbar.setObjectName("main_toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.act_import_xlsx)
        toolbar.addSeparator()
        toolbar.addAction(self.act_flash)
        toolbar.addAction(self.act_pb)
        toolbar.addSeparator()
        toolbar.addAction(self.act_new_result_window)
        toolbar.addAction(self.act_new_dock_result)
    
    def _build_statusbar(self):
        """Создание строки состояния"""
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage("Готово")
        self.setStatusBar(self.status_bar)
    
    def _connect_signals(self):
        """Подключение сигналов"""
        self.core_bridge.status_update.connect(self._log)
        self.core_bridge.error_occurred.connect(self._show_error)
        self.core_bridge.result_ready.connect(self._show_result)
        self.core_bridge.composition_loaded.connect(self._on_composition_loaded)
    
    def _on_composition_loaded(self, composition_data):
        """Обработка загрузки состава"""
        # Обновляем дерево проекта
        n_components = len(composition_data['components'])
        self.composition_item.setText(0, f"Состав: {n_components} компонентов")
        
        if composition_data['has_heavy_components']:
            self.composition_item.setText(0, self.composition_item.text(0) + " (C6+)")
        
        # Показываем таблицу свойств
        self.properties_table.set_composition(self.core_bridge)
        self.properties_dock.show()
        self.act_show_properties.setChecked(True)
        
        # Показываем состав во вкладке
        self._show_composition_tab(composition_data)
    
    def on_import_xlsx(self):
        """Импорт состава из Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл состава", "",
            "Excel files (*.xlsx *.xls);;All files (*)"
        )
        
        if not file_path:
            return
        
        # Диалог параметров импорта
        sheet_name, ok = QInputDialog.getText(self, "Параметры импорта", 
                                               "Имя листа:", text="Sheet1")
        if not ok:
            sheet_name = "Sheet1"
        
        has_header = QMessageBox.question(self, "Заголовки", 
                                          "Первый ряд содержит заголовки?",
                                          QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
        
        try:
            self.core_bridge.import_composition_from_excel(file_path, sheet_name, has_header)
            self._log(f"✅ Состав импортирован: {Path(file_path).name}")
            self.status_bar.showMessage(f"Загружен состав из {Path(file_path).name}")
        except Exception as e:
            self._log(f"❌ Ошибка импорта: {e}")
            self._show_error(f"Не удалось импортировать файл:\n{e}")
    
    def _show_composition_tab(self, composition_data):
        """Отображение состава во вкладке"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Форматируем вывод
        text = "📊 Состав флюида\n" + "="*50 + "\n\n"
        for comp, fraction in composition_data['mole_fractions'].items():
            text += f"{comp:10} : {fraction:.6f} моль.дол.\n"
        
        text += f"\n{'='*50}\n"
        text += f"Всего компонентов: {len(composition_data['components'])}\n"
        if composition_data['has_heavy_components']:
            text += f"Тяжелые компоненты (C6+): {', '.join(composition_data['heavy_components'])}\n"
        
        text_edit.setPlainText(text)
        layout.addWidget(text_edit)
        
        self.central_tabs.addTab(widget, "Состав")
        self.central_tabs.setCurrentWidget(widget)
    
    def on_select_correlations(self):
        """Выбор корреляций критических свойств"""
        if not self.core_bridge.has_composition():
            self._show_error("Сначала импортируйте состав!")
            return
        
        dialog = CorrelationsDialog(self, self.core_bridge.available_correlations)
        if dialog.exec() == QDialog.Accepted:
            correlations = dialog.get_selected_correlations()
            try:
                self.core_bridge.set_critical_properties_correlations(correlations)
                self.correlations_item.setText(0, "Корреляции: выбраны")
                self._log("✅ Корреляции критических свойств установлены")
                
                # Обновляем таблицу свойств
                self.properties_table.refresh_data()
            except Exception as e:
                self._log(f"❌ Ошибка: {e}")
    
    def on_select_eos(self):
        """Выбор уравнения состояния"""
        dialog = EOSDialog(self, self.core_bridge.available_eos)
        if dialog.exec() == QDialog.Accepted:
            eos = dialog.get_selected_eos()
            try:
                self.core_bridge.set_eos(eos)
                self.eos_item.setText(0, f"Уравнение состояния: {eos}")
                self._log(f"✅ Выбрано уравнение состояния: {eos}")
            except Exception as e:
                self._log(f"❌ Ошибка: {e}")
    
    def on_flash_calc(self):
        """Выполнение flash расчета"""
        if not self._check_prerequisites():
            return
        
        # Диалог ввода P, T
        pressure, ok = QInputDialog.getDouble(self, "Flash расчет", 
                                              "Давление (МПа):", value=10, min=0.1, max=100)
        if not ok:
            pressure = 10e6
        else:
            pressure *= 1e6
        
        temperature, ok = QInputDialog.getDouble(self, "Flash расчет", 
                                                 "Температура (K):", value=298.15, min=100, max=1000)
        if not ok:
            temperature = 298.15
        
        try:
            result = self.core_bridge.calculate_flash(pressure, temperature)
            self.flash_item.setText(0, f"Flash расчет: выполнен")
            self.status_bar.showMessage("Flash расчет завершен")
        except Exception as e:
            self._log(f"❌ Ошибка flash расчета: {e}")
    
    def on_pb_calc(self):
        """Расчет давления насыщения"""
        if not self._check_prerequisites():
            return
        
        temperature, ok = QInputDialog.getDouble(self, "Давление насыщения", 
                                                 "Температура (K):", value=298.15, min=100, max=1000)
        if not ok:
            temperature = 298.15
        
        try:
            result = self.core_bridge.calculate_pb(temperature)
            self.pb_item.setText(0, f"Давление насыщения: {result['value_mpa']:.2f} МПа")
            self.status_bar.showMessage(f"Pb = {result['value_mpa']:.2f} МПа")
        except Exception as e:
            self._log(f"❌ Ошибка расчета Pb: {e}")
    
    def _check_prerequisites(self):
        """Проверка необходимых условий для расчета"""
        if not self.core_bridge.has_composition():
            self._show_error("Сначала импортируйте состав!")
            return False
        if not self.core_bridge.eos_type:
            self._show_error("Сначала выберите уравнение состояния!")
            return False
        return True
    
    def _create_result_window(self):
        """Создание окна результатов"""
        window_id = f"result_{len(self.result_windows)}"
        result_window = ResultWindow()
        result_window.setWindowTitle(f"Результаты {len(self.result_windows) + 1}")
        result_window.show()
        self.result_windows[window_id] = result_window
        result_window.destroyed.connect(lambda: self.result_windows.pop(window_id, None))
    
    def _create_result_dock(self):
        """Создание док-панели результатов"""
        dock_id = f"result_dock_{len(self.dock_windows)}"
        dock = DockableResultWindow(f"Результаты {len(self.dock_windows) + 1}", self)
        dock.setObjectName(dock_id)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.dock_windows[dock_id] = dock
        dock.destroyed.connect(lambda: self.dock_windows.pop(dock_id, None))
    
    def _on_project_item_double_clicked(self, item, column):
        """Обработка двойного клика в дереве проекта"""
        text = item.text(column).lower()
        
        if "состав" in text:
            self.on_import_xlsx()
        elif "критические свойства" in text:
            self.on_select_correlations()
        elif "уравнение состояния" in text:
            self.on_select_eos()
        elif "flash" in text:
            self.on_flash_calc()
        elif "давление насыщения" in text:
            self.on_pb_calc()
    
    def _show_result(self, result_data):
        """Отображение результата"""
        # Форматируем результат
        formatted = self._format_result(result_data)
        
        # Показываем в новой вкладке
        widget = QWidget()
        layout = QVBoxLayout(widget)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(formatted)
        layout.addWidget(text_edit)
        
        tab_name = result_data.get('type', 'Результат')
        self.central_tabs.addTab(widget, tab_name)
        self.central_tabs.setCurrentWidget(widget)
    
    def _format_result(self, data, indent=0):
        """Рекурсивное форматирование результата"""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if key == 'type':
                    continue
                prefix = "  " * indent
                lines.append(f"{prefix}• {key}: {self._format_result(value, indent + 1)}")
            return "\n".join(lines)
        elif isinstance(data, float):
            return f"{data:.6f}"
        else:
            return str(data)
    
    def _close_central_tab(self, index):
        """Закрытие вкладки"""
        if index > 0:
            widget = self.central_tabs.widget(index)
            if widget:
                widget.deleteLater()
            self.central_tabs.removeTab(index)
    
    def _log(self, text):
        """Добавление в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f"[{timestamp}] {text}")
        # Автопрокрутка вниз
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )
    
    def _show_error(self, message):
        """Показ ошибки"""
        QMessageBox.critical(self, "Ошибка", message)
        self._log(f"❌ {message}")
    
    def _about(self):
        """О программе"""
        QMessageBox.about(self, "О программе",
                         "Композиционное моделирование флюида\n\n"
                         "Версия: 2.0\n"
                         "Разработано с использованием PySide6\n\n"
                         "Особенности:\n"
                         "• Гибкий интерфейс с док-панелями\n"
                         "• Интеграция с расчетным ядром\n"
                         "• Поддержка тяжелых компонентов (C6+)")
    
    def closeEvent(self, event):
        """Сохранение состояния"""
        self._save_layout()
        for window in self.result_windows.values():
            window.close()
        super().closeEvent(event)
    
    def _save_layout(self):
        """Сохранение геометрии"""
        self.settings.beginGroup(self.SETTINGS_GROUP)
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("state", self.saveState())
        self.settings.endGroup()
    
    def _restore_layout(self):
        """Восстановление геометрии"""
        self.settings.beginGroup(self.SETTINGS_GROUP)
        geometry = self.settings.value("geometry")
        state = self.settings.value("state")
        self.settings.endGroup()
        
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)