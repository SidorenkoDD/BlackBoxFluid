import dearpygui.dearpygui as dpg

dpg.create_context()

def check_boxes_and_enable_windows():
    all_checked = all([
        dpg.get_value("param1"),
        dpg.get_value("param2"),
        dpg.get_value("param3")
    ])
    
    if all_checked:
        dpg.enable_item("CompositionInputWindow")
        dpg.enable_item("FlashInputWindow")
        dpg.set_value("error_msg", "Model defined successfully!")
        dpg.configure_item("error_msg", color=[0, 255, 0])
    else:
        dpg.set_value("error_msg", "Please check all model parameters!")
        dpg.configure_item("error_msg", color=[255, 0, 0])

def reset_windows():
    # Проверяем, существуют ли окна перед отключением
    if dpg.does_item_exist("CompositionInputWindow"):
        dpg.disable_item("CompositionInputWindow")
    if dpg.does_item_exist("FlashInputWindow"):
        dpg.disable_item("FlashInputWindow")

with dpg.window(label="Main Window"):
    with dpg.window(label="Define Model", width=400, height=300):
        dpg.add_checkbox(label="Parameter 1", tag="param1")
        dpg.add_checkbox(label="Parameter 2", tag="param2")
        dpg.add_checkbox(label="Parameter 3", tag="param3")
        dpg.add_button(label="Define Model", callback=check_boxes_and_enable_windows)
        dpg.add_text("", tag="error_msg")
    
    # Создаем окна, но сразу отключаем их
    with dpg.window(label="Composition Input", tag="CompositionInputWindow", width=400, height=300, show=True):
        dpg.add_text("Composition Input Window Content")
        dpg.add_input_text(label="Input")
    
    with dpg.window(label="Flash Input", tag="FlashInputWindow", width=400, height=300, show=True):
        dpg.add_text("Flash Input Window Content")
        dpg.add_input_text(label="Input")

# Отключаем окна после их создания
reset_windows()

dpg.create_viewport(title='Model Definition', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()