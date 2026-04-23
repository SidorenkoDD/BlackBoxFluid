from abc import abstractmethod, ABC
from enum import StrEnum


class EOSType(StrEnum):
    PREOS = 'PREOS'
    SRKEOS = 'SRKEOS'
    BRSEOS = 'BRSEOS'


class EOS(ABC):
    """
    Abstract class for EOS classes
    """
    def __init__(self, composition, p, t):

        self._z = ...
        self._fugacities = ...
        self._p = ...
        self._t = ...

    @abstractmethod
    def calc_eos(self) -> list:
        pass