from abc import abstractmethod, ABC
#from calculations.Composition.Composition import Composition
from typing import Dict, TypeVar, Generic
from calculations.EOS.BaseEOS import EOS


T = TypeVar('T')

class ModuleProperty(Generic[T]):
    """Дескриптор для модулей с type hints"""
    def __get__(self, obj, owner) -> T:
        if obj is None:
            return self
        return obj._modules[self._name]
    
    def __set_name__(self, owner, name):
        self._name = name




class PhaseStabilityTest:
    '''Абстрактный класс для stability test
    '''
    def __init__(self, composition, p, t, eos: EOS | str):
        self.composition = composition
        self.p = p
        self.t = t
        self.eos = eos

        
    @abstractmethod
    def calculate_phase_stability(self) -> dict:
        pass



class Calculator:
    '''Абстрактный класс для расчетного подмодуля (например, TwoPhaseFlash)
    '''

    def __init__(self, composition, eos):
        self.composition = composition
        self.eos = eos
        self.last_result = None
    
    def calculate(self, conditions):
        raise NotImplementedError
    

class CalculationModule:
    '''Абстрактный класс для расчетного модуля (например, Flash)
    '''

    def __init__(self):
        self._calculators = {}
    
    def register_calculator(self, name, calculator):
        self._calculators[name] = calculator
        
    def __getattr__(self, name):
        if name in self._calculators:
            return self._calculators[name]
        raise AttributeError(f"No calculator '{name}' in module")
    
class Reader(ABC):
    '''Abstract class for data reader
    '''
    @abstractmethod
    def load_database(self):
        pass