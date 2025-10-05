from calculations.Experiments.StandardSeparation import StandardSeparation
from calculations.Experiments.SeparatorTest import SeparatorTest
from calculations.Experiments.DL import DL

class ExperimentsFacade:
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos

        self.STANDARDSEPARATION = StandardSeparation(self._composition, self._eos)
        self.SEPARATORTEST = SeparatorTest(self._composition, self._eos)
        self.DL = DL(self._composition, self._eos)
    
        
