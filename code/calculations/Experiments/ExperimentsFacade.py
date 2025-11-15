from calculations.Experiments.StandardSeparation import StandardSeparation
from calculations.Experiments.SeparatorTest import SeparatorTest
from calculations.Experiments.DLE import DLE, DLE_2

class ExperimentsFacade:
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos

        self.STANDARDSEPARATION = StandardSeparation(self._composition, self._eos)
        self.SEPARATORTEST = SeparatorTest(self._composition, self._eos)
        self.DLE = DLE_2(self._composition, self._eos)
    
        
