from abc import abstractmethod, ABC

class EOS(ABC):
    '''Абстрактный класс для EOS
    '''
    def __init__(self, zi, components_properties, p, t):
        self.zi = zi
        self.components_properties = components_properties
        self.p = p
        self.t = t


    @abstractmethod
    def calc_eos(self) -> list:
        pass
    
    
    @abstractmethod
    def return_eos_root_and_fugacities(self) -> float | dict :
        pass