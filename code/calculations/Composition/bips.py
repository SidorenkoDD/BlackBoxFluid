'''Class BIPSCalculator allows to calculate binary interaction points for composition
'''
import math
import pandas as pd
import numpy as np


# class BIPSFactory:
#     def __init__(self, method):
#         self.method = method

#     def calculate(self):
#         if self.method == 'zero':


class BIPSCalculator:
    def __init__(self, composition_dataframe: pd.DataFrame, method : str = 'zero'):
        self.composition_dataframe = composition_dataframe
        self.method = method


    def calculate(self):
        shape = (len(self.composition_dataframe), len(self.composition_dataframe))
        composition_bips = pd.DataFrame(np.zeros(shape=shape))
        composition_bips.index = self.composition_dataframe.index
        composition_bips.columns = self.composition_dataframe.index
        return composition_bips


    def _zero_bips(self):
        return 0

    def _chueh_prausnitz_bip(self, component_i, component_j, A = 0.18, B = 6):
        '''Chew-Parusnitz correlation for BIPS
        '''

        v_ci = self._composition_data['critical_volume'][component_i]
        v_cj = self._composition_data['critical_volume'][component_j]

        return A * (1 - math.pow(((2 * math.pow(v_ci, 1/6) * math.pow(v_cj, 1/6))/(math.pow(v_ci, 1/3) + math.pow(v_cj, 1/3))), B))
    
    def  _calculate_bips(self):
        if len(self._c6_plus_components) > 0:

            # Этот цикл добавляет в уже существующие словари тяжелые компоненты
            for component in [x for x in self._composition.keys() if x not in self._c6_plus_components]:
                for plus_component in self._c6_plus_components:
                    self._composition_data['bip'][component][plus_component] = self._make_all_bips_zero_for_C6_plus()

            # Этот цикл создает новые словари для тяжелых компонент
            for plus_component in self._c6_plus_components:
                comp_dict = {}
                for component in self._composition.keys():
                    comp_dict[component] = round(self._make_all_bips_zero_for_C6_plus(), 3)
                
                self._composition_data['bip'][plus_component] = comp_dict


