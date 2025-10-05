from calculations.Composition.Composition import Composition
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Utils.Errors import LenthMissMatchError, nStagesError
from calculations.Utils.Conditions import Conditions
from calculations.VLE.Flash import FlashFactory


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


