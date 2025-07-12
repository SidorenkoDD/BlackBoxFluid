import dearpygui.dearpygui as dpg
import json
from datetime import datetime

class CompositionsWindow:
    def __init__(self):
        self.compositions = []
        self.load_compositions()
        self.setup_ui()

    def load_compositions(self):
        try:
            with open('compositions.json', 'r') as f:
                self.compositions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.compositions = []

    def save_compositions(self):
        with open('compositions.json', 'w') as f:
            json.dump(self.compositions, f, indent=2)

    def add_composition(self):
        with dpg.window(label="Add Composition", width=400, height=200, modal=True):
            dpg.add_input_text(label="Name", tag="new_comp_name", width=300)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add", callback=self._add_composition_callback)
                dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item(dpg.get_active_window()))

    def _add_composition_callback(self):
        name = dpg.get_value("new_comp_name")
        if name:
            new_comp = {
                "name": name,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.compositions.append(new_comp)
            self.save_compositions()
            self.update_table()
            dpg.delete_item(dpg.get_active_window())

    def edit_composition(self, sender, app_data, user_data):
        with dpg.window(label="Edit Composition", width=400, height=200, modal=True):
            dpg.add_input_text(
                label="Name", 
                tag="edit_comp_name", 
                default_value=self.compositions[user_data]["name"],
                width=300
            )
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Save", 
                    callback=self._edit_composition_callback, 
                    user_data=user_data
                )
                dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item(dpg.get_active_window()))

    def _edit_composition_callback(self, sender, app_data, user_data):
        new_name = dpg.get_value("edit_comp_name")
        if new_name:
            self.compositions[user_data]["name"] = new_name
            self.save_compositions()
            self.update_table()
            dpg.delete_item(dpg.get_active_window())

    def delete_composition(self, sender, app_data, user_data):
        with dpg.window(label="Confirm Delete", width=300, height=100, modal=True):
            dpg.add_text(f"Delete {self.compositions[user_data]['name']}?")
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Yes", 
                    callback=self._delete_composition_callback, 
                    user_data=user_data
                )
                dpg.add_button(label="No", callback=lambda: dpg.delete_item(dpg.get_active_window()))

    def _delete_composition_callback(self, sender, app_data, user_data):
        self.compositions.pop(user_data)
        self.save_compositions()
        self.update_table()
        dpg.delete_item(dpg.get_active_window())

    def update_table(self):
        dpg.delete_item("compositions_table", children_only=True)
        
        for idx, comp in enumerate(self.compositions):
            with dpg.table_row(parent="compositions_table"):
                dpg.add_text(comp["name"])
                dpg.add_text(comp["created_at"])
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Edit",
                        callback=self.edit_composition,
                        user_data=idx,
                        width=80
                    )
                    dpg.add_button(
                        label="Delete",
                        callback=self.delete_composition,
                        user_data=idx,
                        width=80
                    )

    def setup_ui(self):
        with dpg.window(label="Compositions Manager", width=800, height=600):
            # Buttons row
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add Composition", callback=self.add_composition)
                dpg.add_button(label="Refresh", callback=lambda: [self.load_compositions(), self.update_table()])
            
            # Table
            with dpg.table(
                tag="compositions_table",
                header_row=True,
                borders_innerH=True,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
                resizable=True,
                policy=dpg.mvTable_SizingStretchProp
            ):
                dpg.add_table_column(label="Name", width_stretch=True)
                dpg.add_table_column(label="Created At", width_stretch=True)
                dpg.add_table_column(label="Actions", width_stretch=True)
                
                self.update_table()

# Main application
dpg.create_context()
dpg.create_viewport(title='Compositions Manager', width=850, height=650)

compositions_window = CompositionsWindow()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()