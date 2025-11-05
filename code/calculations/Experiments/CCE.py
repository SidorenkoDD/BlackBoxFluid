import pandas as pd
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



    def calculate(self, p_resirvoir : float,
                  temperature : float,
                  pressure_by_stages : list,
                   flash_type = 'TwoPhaseFlash'):
        '''Method calculates CCE between p_start and Pbub with constant temperature.
        
        By default, interpolation between p_start and Pb (automatically calculated) for n_steps
        
        Args
        ----
        * p_resirvoir - reservoir pressure
        * temperature - constant temperature for experiment
        * pressure_by_stages - list with pressure stages
        '''
        result = {}

        def _is_strictly_descending() -> bool:
            '''Method checks descending values for pressure_list'''
            return all(pressure_by_stages[i] < pressure_by_stages[i-1] for i in range(1, len(pressure_by_stages)))


        def _is_p_pres_in_pressure_by_stages_list() -> list:
            '''Method checks is p_res in list, in no, append p_res in list'''

            if p_resirvoir in pressure_by_stages:
                pass
            else:
                pressure_by_stages.append(p_resirvoir)
                pressure_by_stages.sort(reverse=True)

        if _is_strictly_descending():
            _is_p_pres_in_pressure_by_stages_list()
            for p in pressure_by_stages:
                current_conditions = Conditions(p, temperature)
                flash_object = FlashFactory(self._composition, self._eos)
                flash_calculator = flash_object.create_flash(flash_type= flash_type)
                result[current_conditions.p] = flash_calculator.calculate(conditions=current_conditions)
        else:
            raise InvalidPressureSequence(f'pressure_list must be descending only : {pressure_by_stages}')

        self.result = CCEResults(pressure = list(result.keys()),
                                 temperature= temperature,
                                 liquid_volume = [result[x].liquid_volume for x in list(result.keys())],
                                 liquid_density = [result[x].liquid_density for x in list(result.keys())])

        self.dataframe = pd.DataFrame({'Pressure' : self.result.pressure,
                                       'Liquid volume' : self.result.liquid_volume,
                                       'Liquid density' : self.result.liquid_density})

        self._calculate_v_d_vpres(p_reservoir=p_resirvoir)

        return self.result


    def _calculate_compressibility(self):
        ...


    def _calculate_v_d_vpres(self, p_reservoir):
        self.dataframe['V/Vres'] = self.dataframe['Liquid volume'] / self.dataframe[self.dataframe['Pressure'] == p_reservoir]['Liquid volume'].iloc[0]


    def _calculate_v_d_vpsat(self, p_sat):
        self.dataframe['V/Vres'] = self.dataframe['Liquid volume'] / self.dataframe[self.dataframe['Pressure'] == p_sat]['Liquid volume'].iloc[0]
