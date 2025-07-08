import dearpygui.dearpygui as dpg

# Создаем контекст DPG
dpg.create_context()

# Переменные для хранения данных
table_name = ""
table_data = []

def create_table_callback():
    global table_name, table_data
    
    # Получаем имя таблицы из поля ввода
    table_name = dpg.get_value("table_name_input")
    
    # Очищаем предыдущую таблицу, если она была
    if dpg.does_item_exist("table_container"):
        dpg.delete_item("table_container")
    
    # Создаем контейнер для таблицы
    with dpg.group(tag="table_container", parent="main_window"):
        dpg.add_text(f"Table: {table_name}")
        
        # Создаем саму таблицу
        with dpg.table(header_row=True, row_background=True, 
                      borders_innerH=True, borders_outerH=True, borders_innerV=True, 
                      borders_outerV=True, width=400):
            
            # Добавляем колонки
            dpg.add_table_column(label="Comp", width_fixed=True)
            dpg.add_table_column(label="Val", width_fixed=True)
            
            # Добавляем 5 начальных строк
            for i in range(5):
                with dpg.table_row():
                    dpg.add_input_text(default_value=f"T {i+1}", tag=f"text_{i}")
                    dpg.add_input_float(default_value=0.0, tag=f"float_{i}")

        # Кнопка для добавления новых строк
        dpg.add_button(label="Add row", callback=add_row)
        
        # Кнопка для сохранения данных
        dpg.add_button(label="Save", callback=save_data)

def add_row():
    # Получаем текущее количество строк
    row_count = len([item for item in dpg.get_item_children("table_container")[1] if "table_row" in dpg.get_item_type(item)])
    
    # Добавляем новую строку
    with dpg.table_row(parent="table_container"):
        dpg.add_input_text(default_value=f"T {row_count+1}", tag=f"text_{row_count}")
        dpg.add_input_float(default_value=0.0, tag=f"float_{row_count}")

def save_data():
    global table_data
    table_data = []
    
    # Собираем данные из всех строк
    row_count = len([item for item in dpg.get_item_children("table_container")[1] if "table_row" in dpg.get_item_type(item)])
    
    for i in range(row_count):
        text_value = dpg.get_value(f"text_{i}")
        float_value = dpg.get_value(f"float_{i}")
        table_data.append((text_value, float_value))
    
    print("Saved data:")
    print(f"Label: {table_name}")
    for i, (text, number) in enumerate(table_data):
        print(f"String {i+1}: Text = '{text}', Num = {number}")

# Создаем главное окно
with dpg.window(tag="main_window", width=600, height=500):
    dpg.add_text("Create")
    dpg.add_input_text(tag="table_name_input", label="Label", default_value="my_data_1")
    dpg.add_button(label="Add", callback=create_table_callback)

# Настраиваем и запускаем DPG
dpg.create_viewport(title='Res', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()