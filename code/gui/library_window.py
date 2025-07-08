import dearpygui.dearpygui as dpg
import json
from db.db_reader import DBReader
from gui.add_db_window import AddDBWindow
from config import DB_PATH

class LibraryWindow:
    def __init__(self, position: dict):
        self.position = position
        self.tag = "library_window"
        self.db_reader = DBReader(DB_PATH)
        self.add_db_window = AddDBWindow()

    def show(self):
        """Показывает окно библиотеки с таблицей данных."""
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)

        library_keys = self.db_reader.get_keys()

        with dpg.window(
            tag=self.tag,
            label="DB Data",
            width=self.position.get('width', 800),
            height=self.position.get('height', 600),
            pos=(self.position.get('x', 100), self.position.get('y', 100)),
            modal=False,
            no_close=False
        ):
            with dpg.group(horizontal=True):
                # Группа для списка библиотек
                with dpg.group(width=200):
                    dpg.add_text("Select db item:")
                    dpg.add_listbox(
                        tag='listbox_library',
                        items=library_keys,
                        num_items=min(15, len(library_keys)),
                        width=180,
                        callback=self._update_library_table
                    )
                    dpg.add_spacer(height=20)
                    dpg.add_button(label='Add', callback=self.add_db_window.show)
                    dpg.add_button(
                        label="Close",
                        callback=lambda: dpg.delete_item(self.tag)
                    )

                # Группа для таблицы
                with dpg.group(tag="library_table_group"):
                    if library_keys:
                        self._show_selected_library_table(library_keys[0])

    def _show_selected_library_table(self, key: str):
        """Отображает таблицу для выбранного ключа."""
        tag = "library_table"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        data = self.db_reader.get_data(key)
        if not data:
            return

        with dpg.table(
            tag=tag,
            parent="library_table_group",
            header_row=True,
            borders_innerH=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_outerV=True,
            width=550,
            height=500
        ):
            dpg.add_table_column(label="Component")
            dpg.add_table_column(label="Value")

            for key, value in data.items():
                with dpg.table_row():
                    dpg.add_text(str(key))
                    if isinstance(value, (dict, list)):
                        dpg.add_text(json.dumps(value, indent=2, ensure_ascii=False))
                    else:
                        dpg.add_text(str(value))

    def _update_library_table(self, sender):
        """Обновляет таблицу при изменении выбора."""
        selected_key = dpg.get_value(sender)
        self._show_selected_library_table(selected_key)