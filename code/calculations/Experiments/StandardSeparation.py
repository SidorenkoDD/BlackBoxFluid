from calculations.VLE.flash import FlashFactory
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Utils.Conditions import Conditions


class StandardSeparation(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        ...

    def calculate(self, flash_type = 'TwoPhaseFlash'):
        self._flash_object = FlashFactory(self._composition, self._eos)
        self._standard_conditions = Conditions(0.1, 20)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._standard_separation_result = flash_calculator.calculate(conditions=self._standard_conditions)

    @property
    def show_results(self):
        ...