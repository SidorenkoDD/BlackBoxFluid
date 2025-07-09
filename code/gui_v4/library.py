# library.py
import dearpygui.dearpygui as dpg
import json
import yaml
from pathlib import Path
from db_reader import DBReader

class LibraryWindow:
    def __init__(self):
        self.db = DBReader()
        self.keys = self.db.get_keys()
        
    def create(self):
        with dpg.window(
            tag="popup_window",
            label="DB Data",
            width=800,
            height=600,
            modal=False,
            no_close=False
        ):
            with dpg.group(horizontal=True):
                with dpg.group(width=200):
                    dpg.add_text("Select db item:")
                    dpg.add_listbox(
                        tag='listbox_library',
                        items=self.keys,
                        num_items=min(15, len(self.keys)),
                        width=180,
                        callback=self.update_table
                    )
                    dpg.add_spacer(height=20)
                    dpg.add_button(label='Add', callback=AddToDBWindow().show)
                    dpg.add_button(
                        label="Close",
                        callback=lambda: dpg.delete_item("popup_window")
                    )
                with dpg.group(tag="library_table_group"):
                    if self.keys:
                        self.show_table(self.keys[0])

    def show_table(self, key: str):
        if dpg.does_item_exist("library_table"):
            dpg.delete_item("library_table")
            
        data = self.db.get_data(key)
        with dpg.table(
            tag="library_table",
            parent="library_table_group",
            header_row=True,
            borders_innerH=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_outerV=True,
            width=550,
            height=500
        ):
            if not data:
                dpg.add_text("No data available")
                return

            dpg.add_table_column(label="Component")
            dpg.add_table_column(label="Value")

            for key, value in data.items():
                with dpg.table_row():
                    dpg.add_text(str(key))
                    dpg.add_text(json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value))

    def update_table(self, sender):
        selected_key = dpg.get_value(sender)
        self.show_table(selected_key)

class AddToDBWindow:
    def show(self):
        if dpg.does_item_exist("add_to_db_window"):
            dpg.delete_item("add_to_db_window")
            
        with dpg.window(
            tag="add_to_db_window",
            label='Add to db',
            width=800,
            height=600,
            modal=True
        ):
            dpg.add_text('EXAMPLE\n DB Name\n--->"Component": value\n--->...')
            dpg.add_input_text(tag='new_db_part', height=250, multiline=True)
            dpg.add_button(label='Submit', callback=self.add_to_db)

    def add_to_db(self):
        string_to_db = dpg.get_value('new_db_part')
        fixed_yaml_data = string_to_db.replace("\t", "  ")
        new_data_dict = yaml.safe_load(fixed_yaml_data)

        yaml_file = Path("code/db.yaml")
        existing_data = {}
        
        if yaml_file.exists():
            with yaml_file.open('r') as f:
                existing_data = yaml.safe_load(f) or {}
                
        merged_data = {**existing_data, **new_data_dict}
        
        with yaml_file.open('w') as f:
            yaml.dump(merged_data, f, sort_keys=False)
        dpg.delete_item("add_to_db_window")