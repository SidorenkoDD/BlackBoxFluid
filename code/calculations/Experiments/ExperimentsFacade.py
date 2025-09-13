from calculations.Experiments.StandardSeparation import StandardSeparation

class ExperimentsFacade:
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos

        self.STANDARDSEPARATION = StandardSeparation(self._composition, self._eos)
        
