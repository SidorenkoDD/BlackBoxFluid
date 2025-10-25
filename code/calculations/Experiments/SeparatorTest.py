from calculations.Composition.Composition import Composition
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Utils.Errors import LenthMissMatchError, nStagesError
from calculations.Utils.Conditions import Conditions
from calculations.Utils.Results import SeparatorTestResults
from calculations.VLE.flash import FlashFactory

import pandas as pd


class SeparatorTest(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self.result = {}

    def check_stages(self, stages_pressure, stages_temperature):
        if len(stages_pressure) != len(stages_temperature):
            raise LenthMissMatchError(f'{stages_pressure} and {stages_temperature} are different length!')


    def calculate(self, stages_pressure: list, stages_temperature: list, flash_type = 'TwoPhaseFlash'):
        if len(stages_pressure) != len(stages_temperature):
            raise LenthMissMatchError(f'{stages_pressure} and {stages_temperature} are different length!')
        else:
            for i, stage_pressure in enumerate(stages_pressure):
                self._flash_object = FlashFactory(self._composition, self._eos)
                self._standard_conditions = Conditions(stage_pressure, stages_temperature[i])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.result[f"Stage {i+1}"] = flash_calculator.calculate(conditions=self._standard_conditions)

    def calculate_3stages(self, stages_pressure: list, stages_temperature: list, flash_type = 'TwoPhaseFlash'):
        if len(stages_pressure) != len(stages_temperature):
            raise LenthMissMatchError(f'{stages_pressure} and {stages_temperature} are different length!')
        elif (len(stages_pressure) != 3) or  (len(stages_temperature) != 3):
            raise nStagesError('This method allows to calculate 3 stages only!')

        else:
                # Здесь расчет первой ступени
                self._flash_object = FlashFactory(self._composition, self._eos)
                self.first_stage_conditions = Conditions(stages_pressure[0], stages_temperature[0])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.first_stage_result = flash_calculator.calculate(conditions=self.first_stage_conditions)

                # Начинаем расчет второй ступени
                self.second_stage_composition = Composition(self.first_stage_result.liquid_composition)
                self.second_stage_composition._composition_data = self._composition._composition_data
                self._flash_object = FlashFactory(self.second_stage_composition, self._eos)
                self.second_stage_conditions = Conditions(stages_pressure[1], stages_temperature[1])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.second_stage_result = flash_calculator.calculate(conditions=self.second_stage_conditions)

                # Расчет третьей ступени
                self.third_stage_composition = Composition(self.second_stage_result.liquid_composition)
                self.third_stage_composition._composition_data = self._composition._composition_data
                self._flash_object = FlashFactory(self.third_stage_composition, self._eos)
                self.third_stage_conditions = Conditions(stages_pressure[2], stages_temperature[2])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.third_stage_result = flash_calculator.calculate(conditions=self.third_stage_conditions)


        self.result = SeparatorTestResults(first_stage_pressure = self.first_stage_conditions.p,
                                      first_stage_temperature = self.first_stage_conditions.t,
                                      first_stage_fv = self.first_stage_result.Fv,
                                      first_stage_fl = self.first_stage_result.Fl,
                                      first_stage_vapour_composition = self.first_stage_result.vapour_composition,
                                      first_stage_liquid_composition = self.first_stage_result.liquid_composition,
                                      first_stage_liquid_z = self.first_stage_result.liquid_z,
                                      first_stage_vapour_z = self.first_stage_result.vapour_z,
                                      first_stage_k_values = self.first_stage_result.Ki,
                                      first_stage_vapour_mw = self.first_stage_result.vapour_molecular_mass,
                                      first_stage_liquid_mw = self.first_stage_result.liquid_molecular_mass,
                                      first_stage_vapour_volume = self.first_stage_result.vapour_volume,
                                      first_stage_liquid_volume = self.first_stage_result.liquid_volume,
                                      first_stage_vapour_density = self.first_stage_result.vapour_density,
                                      first_stage_liquid_density = self.first_stage_result.liquid_density,
                                    
                                      second_stage_pressure = self.second_stage_conditions.p,
                                      second_stage_temperature = self.second_stage_conditions.t,
                                      second_stage_fv = self.second_stage_result.Fv,
                                      second_stage_fl = self.second_stage_result.Fl,
                                      second_stage_vapour_composition = self.second_stage_result.vapour_composition,
                                      second_stage_liquid_composition = self.second_stage_result.liquid_composition,
                                      second_stage_liquid_z = self.second_stage_result.liquid_z,
                                      second_stage_vapour_z = self.second_stage_result.vapour_z,
                                      second_stage_k_values = self.second_stage_result.Ki,
                                      second_stage_vapour_mw = self.second_stage_result.vapour_molecular_mass,
                                      second_stage_liquid_mw = self.second_stage_result.liquid_molecular_mass,
                                      second_stage_vapour_volume = self.second_stage_result.vapour_volume,
                                      second_stage_liquid_volume = self.second_stage_result.liquid_volume,
                                      second_stage_vapour_density = self.second_stage_result.vapour_density,
                                      second_stage_liquid_density = self.second_stage_result.liquid_density,

                                      third_stage_pressure = self.third_stage_conditions.p,
                                      third_stage_temperature = self.third_stage_conditions.t,
                                      third_stage_fv = self.third_stage_result.Fv,
                                      third_stage_fl = self.third_stage_result.Fl,
                                      third_stage_vapour_composition = self.third_stage_result.vapour_composition,
                                      third_stage_liquid_composition = self.third_stage_result.liquid_composition,
                                      third_stage_liquid_z = self.third_stage_result.liquid_z,
                                      third_stage_vapour_z = self.third_stage_result.vapour_z,
                                      third_stage_k_values = self.third_stage_result.Ki,
                                      third_stage_vapour_mw = self.third_stage_result.vapour_molecular_mass,
                                      third_stage_liquid_mw = self.third_stage_result.liquid_molecular_mass,
                                      third_stage_vapour_volume = self.third_stage_result.vapour_volume,
                                      third_stage_liquid_volume = self.third_stage_result.liquid_volume,
                                      third_stage_vapour_density = self.third_stage_result.vapour_density,
                                      third_stage_liquid_density = self.third_stage_result.liquid_density)

        return self.result

    @property
    def gas_compositions(self):
        return pd.DataFrame({f'First Stage\n P:{self.first_stage_conditions.p}, T {self.first_stage_conditions.t}': self.result.first_stage_vapour_composition,
                             f'Second Stage\n P:{self.second_stage_conditions.p}, T {self.second_stage_conditions.t}': self.result.second_stage_vapour_composition,
                             f'Third Stage\n P:{self.third_stage_conditions.p}, T {self.third_stage_conditions.t}': self.result.third_stage_vapour_composition,})