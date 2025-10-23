from abc import abstractmethod, ABC

class EOS(ABC):
    '''Abstract class for EOS classes
    '''
    def __init__(self, composition_dataframe, bips, p, t):
        self.composition_dataframe = composition_dataframe
        self.bips = bips
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