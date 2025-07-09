import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Node Editor with Combo"):
    with dpg.node_editor(tag="node_editor"):
        # Узел с выпадающим списком
        with dpg.node(tag="Molecular_mass", label="Molecular_mass"):
            # Входной атрибут с combo
            with dpg.node_attribute(tag="node1_in", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_combo(items=["Option 1", "Option 2", "Option 3"], 
                            default_value="Option 1",
                            tag="node1_combo",
                            width=120)
            
            # Выходной атрибут
            with dpg.node_attribute(tag="node1_out", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("Output")
        
        with dpg.node(tag="pcrit", label="P crit"):
            # Входной атрибут с combo
            with dpg.node_attribute(tag="node2_in", attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_combo(items=["Option 1", "Option 2", "Option 3"], 
                            default_value="Option 1",
                            tag="node2_combo",
                            width=120)
            
            # Выходной атрибут
            with dpg.node_attribute(tag="node2_out", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("Output")
            
        with dpg.node(tag="tcrit", label="T crit"):
            # Входной атрибут с combo
            with dpg.node_attribute(tag="node3_in", attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_combo(items=["Option 1", "Option 2", "Option 3"], 
                            default_value="Option 1",
                            tag="node3_combo",
                            width=120)
            
            # Выходной атрибут
            with dpg.node_attribute(tag="node3_out", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("Output")

        with dpg.node(tag="eos", label="EOS"):
            # Входной атрибут с combo
            with dpg.node_attribute(tag="node4_in", attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_combo(items=["Option 1", "Option 2", "Option 3"], 
                            default_value="Option 1",
                            tag="node4_combo",
                            width=120)
            
            # Выходной атрибут
            with dpg.node_attribute(tag="node4_out", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("Output")

dpg.create_viewport(title='Node Editor with Combo', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()