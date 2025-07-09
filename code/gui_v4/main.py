# main.py
import dearpygui.dearpygui as dpg
from compositional import show_compositional_interface
from library import LibraryWindow
from flash_calculator import FlashCalculator

flash_calc = FlashCalculator()

def menu_callback(sender, app_data, user_data):
    print(f"Selected menu item: {user_data}")

def setup_main_menu():
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            with dpg.menu(label='New'):
                with dpg.menu(label='PVT'):
                    dpg.add_menu_item(label='BO', enabled=False)
                    dpg.add_menu_item(
                        label='Compositional',
                        callback=lambda: show_compositional_interface(flash_calc)
                    )
            dpg.add_menu_item(label="Open", user_data="Open", enabled=False)
            dpg.add_menu_item(label="Save", user_data="Save", enabled=False)
            dpg.add_separator()
            dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

        with dpg.menu(label="Extensions"):
            dpg.add_menu_item(label="Import extension", enabled=False)
        
        with dpg.menu(label="Library"):
            dpg.add_menu_item(label="Open DB", callback=LibraryWindow().create)

        with dpg.menu(label="Info"):
            dpg.add_menu_item(label="About", enabled=False)

def initialize_application():
    dpg.create_context()
    dpg.create_viewport(title="PVT Flash Calculator", width=850, height=700)
    
    with dpg.window(label="Main Window", tag="primary_window"):
        setup_main_menu()
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    initialize_application()