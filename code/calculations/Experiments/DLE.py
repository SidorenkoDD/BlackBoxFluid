from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Composition.Composition import Composition
from calculations.VLE.flash import FlashFactory
from calculations.Utils.Conditions import Conditions
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation

import numpy as np

class DLE(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self.result = {}
        self.fl = []

    def calculate(self, temperature : float, pressure_list : list | None = None,
                   n_steps : float = 10, flash_type = 'TwoPhaseFlash'):
        pb_obj = SaturationPressureCalculation(self._composition,p_max=40, temp= temperature)
        pb = pb_obj.sp_convergence_loop(self._eos)

        if pressure_list is None:
            pressure_array = np.linspace(pb, 0.1, n_steps)
            print(pressure_array)
            print(pressure_array[1:])
            flash_object = FlashFactory(self._composition, self._eos)
            flash_calculator = flash_object.create_flash(flash_type= flash_type)
            #расчет для первого значения давления
            first_step_conditions = Conditions(pressure_array[0], temperature)
            self.result[f'{first_step_conditions.p}_{first_step_conditions.t}'] = flash_calculator.calculate(conditions=first_step_conditions)
            # создаем атрибут состав, который далее будем менять
            self.liquid_composition = self.result[f'{first_step_conditions.p}_{first_step_conditions.t}'].liquid_composition
            # создаем атрибут доля жидкости, который далее будет меняться по ступеням
            self.fl.append(self.result[f'{first_step_conditions.p}_{first_step_conditions.t}'].Fl)

            for pressure in pressure_array[1:]:
                self.liquid_composition = Composition(self.liquid_composition)
                self.liquid_composition._composition_data = self._composition._composition_data
                self._flash_object = FlashFactory(self.liquid_composition, self._eos)
                flash_calculator = self._flash_object.create_flash(flash_type = flash_type)
                current_conditions = Conditions(pressure, temperature)
                self.result[f'{current_conditions.p}_{current_conditions.t}']= flash_calculator.calculate(conditions = current_conditions)
                self.fl.append(self.result[f'{current_conditions.p}_{current_conditions.t}'].Fl)
                self.liquid_composition = self.result[f'{current_conditions.p}_{current_conditions.t}'].liquid_composition
                
            flash_object = FlashFactory(self._composition, self._eos)
            flash_calculator = flash_object.create_flash(flash_type= flash_type)
            #расчет для первого значения давления
            last_step_conditions = Conditions(0.1, 20)
            self.result[f'{last_step_conditions.p}_{last_step_conditions.t}'] = flash_calculator.calculate(conditions=last_step_conditions)

        else:
            ...
