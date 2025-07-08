import dearpygui.dearpygui as dpg

class ResultsWindow:
    @staticmethod
    def show(results: str, position: dict):
        """Отображает окно с результатами расчёта."""
        tag = "results_window"
        
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

        with dpg.window(
            label='Flash Calculation Results',
            tag=tag,
            width=position['width'],
            height=position['height'],
            pos=(position['x'], position['y']),
            no_resize=False,
            no_collapse=False,
            no_close=True
        ):
            dpg.add_input_text(
                multiline=True,
                height=280,
                width=380,
                default_value=results,
                readonly=True,
                tag='flash_results_output'
            )