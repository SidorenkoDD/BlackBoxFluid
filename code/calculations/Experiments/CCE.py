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
        pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= temperature)
        pb = pb_obj.sp_convergence_loop(self._eos)

        def _is_strictly_descending() -> bool:
            '''Method checks descending values for pressure_list'''
            return all(pressure_by_stages[i] < pressure_by_stages[i-1] for i in range(1, len(pressure_by_stages)))

        def _is_p_sat_in_pressure_by_stages_list() -> list:
            '''Method checks is p_sat in list, if no, append p_sat in list'''
            pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= temperature)
            pb = pb_obj.sp_convergence_loop(self._eos)
            if pb in pressure_by_stages:
                pass
            else:
                pressure_by_stages.append(pb)
                pressure_by_stages.sort(reverse=True)

        def _is_p_pres_in_pressure_by_stages_list() -> list:
            '''Method checks is p_res in list, in no, append p_res in list'''
            if p_resirvoir in pressure_by_stages:
                pass
            else:
                pressure_by_stages.append(p_resirvoir)
                pressure_by_stages.sort(reverse=True)

        if _is_strictly_descending():
            _is_p_pres_in_pressure_by_stages_list()
            _is_p_sat_in_pressure_by_stages_list()
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

        self.dataframe.index = self._create_index_to_df(p_list=pressure_by_stages, psat=pb, pres= p_resirvoir)
        self._calculate_v_d_vpres(p_reservoir=p_resirvoir)
        self._calculate_v_d_vpsat(p_sat= pb)
        self._calculate_compressibility()

        return self.result

    def _create_index_to_df(self, p_list, psat, pres):
        index = []
        for p in p_list:
            if (p != psat) and p != pres:
                index.append(None)
            elif p == psat:
                index.append('Psat')
            elif p == pres:
                index.append('Pres')
        
        return index


    def _calculate_compressibility(self):
        work_df = self.dataframe.copy()
        work_df['diff_vol'] = work_df['Liquid volume'].diff()
        work_df['sum_vol'] = work_df['Liquid volume'] + work_df['Liquid volume'].shift(1)
        work_df['diff_p'] = work_df['Pressure'].diff()
        work_df['Compressibility'] = - (work_df['diff_vol'] / ((work_df['Liquid volume'])* work_df['diff_p'])) # * 10 **4 #work_df['sum_vol']

        if 'Psat' in work_df.index:
            psat_position = work_df.index.get_loc('Psat')
            
            if psat_position < len(work_df.index) - 1:
                # Используем iloc для позиционного доступа
                work_df.iloc[psat_position + 1:, work_df.columns.get_loc('Compressibility')] = None

        self.dataframe['Compressibility'] = work_df['Compressibility']
        return work_df


    def _calculate_v_d_vpres(self, p_reservoir):
        self.dataframe['V/Vres'] = self.dataframe['Liquid volume'] / self.dataframe[self.dataframe['Pressure'] == p_reservoir]['Liquid volume'].iloc[0]


    def _calculate_v_d_vpsat(self, p_sat):
        self.dataframe['V/Vsat'] = self.dataframe['Liquid volume'] / self.dataframe[self.dataframe['Pressure'] == p_sat]['Liquid volume'].iloc[0]
