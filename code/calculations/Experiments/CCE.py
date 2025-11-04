import numpy as np
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.VLE.flash import FlashFactory
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation
from calculations.Utils.Conditions import Conditions
from calculations.Utils.Errors import InvalidPressureSequence
from calculations.Utils.Results import CCEResults


class CCE(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self.result = None



    def calculate(self, p_start : float, temperature : float, pressure_list : list | None = None,
                   n_steps : float = 10, flash_type = 'TwoPhaseFlash'):
        '''Method calculates CCE between p_start and Pbub with constant temperature.
        
        By default, interpolation between p_start and Pb (automatically calculated) for n_steps
        
        Args
        ----
        * p_start - first stage pressure.
        * temperature - constant temperature for experiment
        * pressure_list - optional to define pressure stages
        * n_steps - points for interpolation, by default 10
        '''
        result = {}
        if pressure_list is None:
            pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= temperature)
            pb = pb_obj.sp_convergence_loop(self._eos)
            pressure_array = np.linspace(p_start, pb, n_steps)
            for p in pressure_array:
                current_conditions = Conditions(p, temperature)
                flash_object = FlashFactory(self._composition, self._eos)
                flash_calculator = flash_object.create_flash(flash_type= flash_type)
                result[current_conditions.p] = flash_calculator.calculate(conditions=current_conditions)
        else:
            def _is_strictly_descending() -> bool:
                '''Method checks descending values for pressure_list'''
                return all(pressure_list[i] < pressure_list[i-1] for i in range(1, len(pressure_list)))
            
            if _is_strictly_descending():
                for p in pressure_list:
                    current_conditions = Conditions(p, temperature)
                    flash_object = FlashFactory(self._composition, self._eos)
                    flash_calculator = flash_object.create_flash(flash_type= flash_type)
                    result[current_conditions.p] = flash_calculator.calculate(conditions=current_conditions)
            else:
                raise InvalidPressureSequence(f'pressure_list must be descending only : {pressure_list}')

        self.result = CCEResults(pressure = list(result.keys()),
                                 temperature= temperature,
                                 liquid_volume = [result[x].liquid_volume for x in list(result.keys())],
                                 liquid_density = [result[x].liquid_density for x in list(result.keys())])

        return self.result


    def _calculate_compressibility(self):
        ...


    def _calculate_v_d_vpres(self):
        ...


    def _calculate_v_d_vpsat(self):
        ...
