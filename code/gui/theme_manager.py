# theme_manager.py
import dearpygui.dearpygui as dpg

class ThemeManager:
    """Управление темами и стилями приложения"""
    
    @staticmethod
    def setup_global_theme():
        """Настройка глобальной темы приложения"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 6, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
        
        dpg.bind_theme(global_theme)
    
    @staticmethod
    def create_color_text(color: tuple) -> dpg.theme:
        """Создание темы для цветного текста"""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, color)
        return theme