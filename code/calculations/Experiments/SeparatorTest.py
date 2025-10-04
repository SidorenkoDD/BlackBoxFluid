from calculations.Experiments.BaseExperiment import PVTExperiment

class SeparatorTest(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
    

    def calculate(self, stages_pressure: list, stages_temperature: list):
        if len(stages_pressure) != len(stages_temperature):
            raise IndexError('Length missmatch')
        else:
            ...