from abc import abstractmethod, ABC
from calculations.Composition.Composition import Composition
from calculations.EOS.BaseEOS import EOS


class PhaseStabilityTest:
    '''Абстрактный класс для stability test
    '''
    def __init__(self, composition:Composition, p, t, eos: EOS | str):
        self.composition = composition
        self.p = p
        self.t = t
        self.eos = eos

        
    @abstractmethod
    def calculate_phase_stability(self) -> dict:
        pass