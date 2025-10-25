from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.VLE.flash import FlashFactory
from calculations.Utils.Conditions import Conditions
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation

import numpy as np

class DLE(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        ...

    def calculate(self, temperature : float, pressure_list : list | None = None,
                   n_steps : float = 10, flash_type = 'TwoPhaseFlash'):
        pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= temperature)
        pb = pb_obj.sp_convergence_loop(self._eos)

        if pressure_list is None:
            pressure_array = np.linspace(pb, 0.1, n_steps)
            for pressure in pressure_array:
                self._flash_object = FlashFactory(self._composition, self._eos)
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                current_conditions = Conditions(pressure, temperature)
                
                self._standard_separation_result = flash_calculator.calculate(conditions=self._standard_conditions)
        else:
            ...
        self._flash_object = FlashFactory(self._composition, self._eos)
        self._standard_conditions = Conditions(0.1, 20)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._standard_separation_result = flash_calculator.calculate(conditions=self._standard_conditions)