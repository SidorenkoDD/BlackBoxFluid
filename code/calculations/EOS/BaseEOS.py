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
    
    # Будто не нужно, реализовано через property
    # @abstractmethod
    # def return_eos_root_and_fugacities(self) -> float | dict :
    #     pass

    @abstractmethod
    #@property
    def z(self) -> float:
        return self._z
    
    @abstractmethod
    #@property
    def fugacities(self) -> dict:
        return self._fugacities