from abc import abstractmethod, ABC

class EOS(ABC):
    '''Abstract class for EOS classes
    '''
    def __init__(self, zi, components_properties, p, t):
        self.zi = zi
        self.components_properties = components_properties
        self.p = p
        self.t = t
        self._z = 0
        self._fugacities = {}


    @abstractmethod
    def calc_eos(self) -> list:
        pass
    


    @abstractmethod
    def z(self) -> float:
        return self._z
    
    @abstractmethod
    def fugacities(self) -> dict:
        return self._fugacities