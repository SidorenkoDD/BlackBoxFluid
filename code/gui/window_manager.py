import dearpygui.dearpygui as dpg
from typing import Dict

class WindowManager:
    """Управляет созданием и уничтожением окон."""
    _windows: Dict[str, object] = {}
    
    @classmethod
    def register_window(cls, tag: str, window: object):
        """Регистрирует окно в менеджере."""
        cls._windows[tag] = window
    
    @classmethod
    def get_window(cls, tag: str):
        """Возвращает экземпляр окна по тегу."""
        return cls._windows.get(tag)
    
    @classmethod
    def close_window(cls, tag: str):
        """Закрывает окно по тегу."""
        if tag in cls._windows:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
            del cls._windows[tag]
    
    @classmethod
    def close_all(cls):
        """Закрывает все зарегистрированные окна."""
        for tag in list(cls._windows.keys()):
            cls.close_window(tag)