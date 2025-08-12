# import pandas as pd
from BaseClasses import ModuleProperty
from Composition import Composition
from Flash import FlashModule
from Conditions import Conditions



# class CompositionalModel:
#     def __init__(self, zi: Composition, eos: str = 'PREOS'):
#         object.__setattr__(self, '_composition', zi)  # Безопасная установка
#         object.__setattr__(self, '_eos', eos)
#         object.__setattr__(self, '_modules', {})
#         self._init_default_modules()
    
#     def _init_default_modules(self):
#         """Инициализация модулей с гарантией отсутствия рекурсии"""
#         self.add_module('flash', FlashModule(self._composition, self._eos))
    
#     def add_module(self, name: str, module):
#         """Добавление модуля с проверкой"""
#         if hasattr(self.__class__, name):
#             raise AttributeError(f"Can't add module '{name}': conflicts with class attribute")
#         self._modules[name] = module
    
#     def __getattr__(self, name):
#         """Доступ к модулям только если атрибут не найден стандартным способом"""
#         if '_modules' in vars(self) and name in self._modules:
#             return self._modules[name]
#         raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
#     def __setattr__(self, name, value):
#         """Запрет на перезапись модулей через присваивание"""
#         if '_modules' in vars(self) and name in self._modules:
#             raise AttributeError(f"Can't modify module '{name}' directly")
#         super().__setattr__(name, value)
    
#     def __dir__(self):
#         """Полный список атрибутов для автодополнения"""
#         return list(self._modules.keys()) + super().__dir__()
        

# from typing import Dict, Any, Optional

# class CompositionalModel:
#     __slots__ = ('_composition', '_eos', '_modules')
    
#     # Аннотации для IDE (необязательно, но улучшает подсказки)
#     flash: 'FlashModule'
#     #viscosity: Optional['ViscosityModule']  # Для будущих модулей
    
#     def __init__(self, zi: 'Composition', eos: str = 'PREOS'):
#         object.__setattr__(self, '_composition', zi)
#         object.__setattr__(self, '_eos', eos)
#         object.__setattr__(self, '_modules', {})
#         self._init_default_modules()
    
#     def _init_default_modules(self):
#         """Инициализация модулей с аннотациями для IDE"""
#         from Flash import FlashModule  # Импорт здесь чтобы избежать циклических зависимостей
#         self.add_module('flash', FlashModule(self._composition, self._eos))
    
#     def add_module(self, name: str, module: Any) -> None:
#         if hasattr(self, name):
#             raise AttributeError(f"Attribute '{name}' already exists")
#         self._modules[name] = module
#         # Динамически добавляем атрибут для IDE
#         setattr(self.__class__, name, property(lambda self, n=name: self._modules[n]))
    
#     def __dir__(self):
#         """Возвращает список атрибутов для автодополнения"""
#         return list(self._modules.keys()) + super().__dir__()


# class CompositionalModel:
#     __slots__ = ('_composition', '_eos', '_modules')
    
#     # Явные аннотации для IDE (теперь подсказки будут работать!)
#     flash: FlashModule  # Указываем конкретный тип модуля
    
#     def __init__(self, zi: 'Composition', eos: str = 'PREOS'):
#         object.__setattr__(self, '_composition', zi)
#         object.__setattr__(self, '_eos', eos)
#         object.__setattr__(self, '_modules', {})
#         self._init_default_modules()
    
#     def _init_default_modules(self):
#         """Инициализация с сохранением типа"""
#         from Flash import FlashModule  # Ленивый импорт
#         self.add_module('flash', FlashModule(self._composition, self._eos))
    
#     def add_module(self, name: str, module: Any):
#         if hasattr(self.__class__, name):
#             raise AttributeError(f"Атрибут '{name}' уже существует")
#         self._modules[name] = module
#         # Динамически создаем property с типом
#         setattr(self.__class__, name, ModuleProperty[type(module)]())


from Composition import Composition
from FlashFactory import FlashFactory
from Flash import FlashFasade
from Conditions import Conditions



class CompositionalModel:
    def __init__(self,zi: Composition, eos: str = 'PREOS', flash_type = 'TwoPhaseFlash'):
        self.composition = zi
        self.eos = eos
        self.flash_name = flash_type
        self.flash = FlashFasade(self.composition, self.eos)
    

if __name__ == '__main__':


    comp = Composition({'C1': 0.5, 'C3': 0.4,  'C9':0.1},
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'kesler_lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'Edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'}
                       )




    comp_model = CompositionalModel(comp, eos = 'PREOS')

    conditions = Conditions(6, 50)

    # from Flash import TwoPhaseFlash
    # comp_model.add_module('flash', TwoPhaseFlash)
    # print(comp_model.__dict__)

    comp_model.flash.TwoPhaseFlash.calculate(conditions=conditions)

    # comp_model.flash.calculate_flash(conditions)
    # comp_model.flash.show_results()

    



    

    



    




    