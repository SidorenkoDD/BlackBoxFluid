from abc import ABC, abstractmethod
from Composition import Composition
from InterfaceEOS import EOS

class PhaseStabilityTest:
    def __init__(self, composition:Composition, p, t, eos: EOS | str):
        self.composition = composition
        self.p = p
        self.t = t
        self.eos = eos

        


    @abstractmethod
    def calculate_phase_stability(self) -> dict:
        pass