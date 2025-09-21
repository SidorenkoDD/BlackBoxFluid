
import dearpygui.dearpygui as dpg



class MainWindow:
    def __init__(self):
        dpg.create_context()  # Создаем контекст DearPyGui

    def create(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="Model"):
                dpg.add_menu_item(label="New",)
                dpg.add_menu_item(label="Open", )
                dpg.add_separator()
                dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())
            
            with dpg.menu(label="Edit"):
                dpg.add_menu_item(label="Cut", )
                dpg.add_menu_item(label="Copy", )
                dpg.add_menu_item(label="Paste",)
            

            with dpg.menu(label = 'Experiments'):
                dpg.add_menu_item(label='Standard Separation')
                dpg.add_menu_item(label='CCE')
                dpg.add_menu_item(label= 'DLE')
                dpg.add_menu_item(label= 'Separator Test')

            with dpg.menu(label = "Flash & Process"):
                dpg.add_menu_item(label='Flash')
                dpg.add_menu_item(label='Saturation Pressure')


        # Главное окно приложения
        with dpg.window(label="Main Window", tag="main_window", 
                    width=800, height=600, pos=(0, 0)):
            dpg.add_text("This is the main content area")
            dpg.add_button(label="Click me!")

        dpg.create_viewport(title='My Application', width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def exit_app(self):
        dpg.stop_dearpygui()

if __name__ == '__main__':
    main = MainWindow()
    main.create()