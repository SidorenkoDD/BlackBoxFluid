from abc import abstractmethod, ABC
from ..Composition.CompositionV2 import Composition
from ..EOS.BaseEOS import EOS


class PhaseStabilityTest(ABC):
    """
    Абстрактный класс для Stability Test
    """
    def __init__(self, composition:Composition, p, t, eos: EOS | str):
        self.composition = composition
        self.p = p
        self.t = t
        self.eos = eos

    @abstractmethod
    def calculate_phase_stability(self) -> dict:
        pass
