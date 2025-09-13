from calculations.Experiments.BaseExperiment import PVTExperiment

class SeparatorTest(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos

    def calculate(self):
        ...