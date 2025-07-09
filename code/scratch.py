import dearpygui.dearpygui as dpg
from dearpygui import demo

dpg.create_context()
demo.show_demo()  # Это откроет демо-окно со всеми возможностями DPG
dpg.create_viewport(title="Dear PyGui Demo", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()