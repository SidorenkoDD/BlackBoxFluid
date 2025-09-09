from pathlib import Path
import sys

# Добавляем корневую директорию в PYTHONPATH
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))


from calculations.Composition.PlusComponentCorrelations import PlusComponentProperties
from calculations.Utils.JsonDBReader import JsonDBReader
import math
import json
import pandas as pd
import re

class Composition:
    ''' Класс для хранения и обработки состава флюида
    

    Attributes:

    ----------
        * zi - словарь с компонентами и их мольной долей

    Methods:
    -------

        * validate_composition_sum - метод проверки суммы компонентов (граница по диапазону 0.999 <= sum_of_components <= 1)
        * validate_c7_plus_components - метод определяет, есть ли С6+ компоненты в исходном составе. Если да, то производится дополнительный расчет свойств для тяжелых компонентов
        * create_composition_db - метод создает словарь, в котором будут храниться параметры компонент
    '''

    def __init__(self,  zi:dict, c6_plus_bips_correlation = None, 
                 c6_plus_correlations: dict = {'critical_temperature': 'Kesler_Lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'Edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'}):

        self._composition = zi
        self._c6_plus_correlations = c6_plus_correlations
        self._c6_plus_bips_correlation = c6_plus_bips_correlation

        self._validate_composition_sum()
        self._validate_c6_plus_components()
        self._create_composition_db()
        self._calculate_bips()
        self._prepare_composition_data()


    def _validate_composition_sum(self):
        '''Method checks sum of components, range 0.998 to 1.001
        '''
        sum_of_components = sum(self._composition.values())
        if not 0.997 <= sum_of_components <=1.002:
            raise ValueError('Сумма компонент не равна 1')


    def _validate_c6_plus_components(self):
        '''Метод определяет, есть ли С6+ компоненты в составе.
        Если есть, то рассчитывается и формируется единый словарь свойств для конкретного состава.
        '''

        def extract_number_from_end(text):
            match = re.search(r'(\d+)$', text)
            if match:
                return int(match.group(1))
            return 0
        _c6_plus_components = [item for item in self._composition.keys() if extract_number_from_end(item) > 6]
        self._c6_plus_components = _c6_plus_components
        
    
    def _create_composition_db(self):
        '''Method creates component properties for composition,  loading from json
        '''
        jsondbreader = JsonDBReader()
        self._composition_data = jsondbreader.load_database()
        # with open(r'code/db/new_db.json') as f:
        #     self.composition_data = json.load(f)


        if len(self._c6_plus_components) > 0:


            for component in self._c6_plus_components:
                cur_comp_properties = PlusComponentProperties(component, correlations_config= self._c6_plus_correlations)
                cur_comp_properties.calculate_all_props_v2()

                self._composition_data['molar_mass'][component] = cur_comp_properties.data['M']
                self._composition_data['critical_pressure'][component] = cur_comp_properties.data['p_c']
                self._composition_data['critical_temperature'][component] = cur_comp_properties.data['t_c']
                self._composition_data['acentric_factor'][component] = cur_comp_properties.data['acentric_factor']
                self._composition_data['critical_volume'][component] = cur_comp_properties.data['crit_vol']
                self._composition_data['shift_parameter'][component] = cur_comp_properties.data['Cpen']


    def _chueh_prausnitz_bip(self, component_i, component_j, A = 0.18, B = 6):
        '''Chew-Parusnitz correlation for BIPS
        '''

        v_ci = self._composition_data['critical_volume'][component_i]
        v_cj = self._composition_data['critical_volume'][component_j]

        return A * (1 - math.pow(((2 * math.pow(v_ci, 1/6) * math.pow(v_cj, 1/6))/(math.pow(v_ci, 1/3) + math.pow(v_cj, 1/3))), B))


    def _make_all_bips_zero_for_C6_plus(self):
        '''returns 0 for bips'''
        return 0


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


    def _prepare_composition_data(self):
        '''Method generates composition db with C6+ components
        '''
        filtered_data = {}
        
        for main_key, inner_dict in self._composition_data.items():
            if isinstance(inner_dict, dict):
                # Для обычных вложенных словарей
                filtered_inner = {}
                for component, value in inner_dict.items():
                    if component in self._composition.keys():
                        filtered_inner[component] = value
                filtered_data[main_key] = filtered_inner
            else:
                # Если значение не словарь, оставляем как есть
                filtered_data[main_key] = inner_dict
        if 'bip' in self._composition_data.keys():
            bip_dict = self._composition_data['bip']
            filtered_bip = {}
            for comp1 in bip_dict:
                if comp1 in self._composition:
                    filtered_inner_bip = {}
                    for comp2, value in bip_dict[comp1].items():
                        if comp2 in self._composition:
                            filtered_inner_bip[comp2] = value
                    if filtered_inner_bip:  # добавляем только если есть значения
                        filtered_bip[comp1] = filtered_inner_bip
            filtered_data['bip'] = filtered_bip

        self._composition_data = filtered_data


    def edit_component_properties(self, component: str, properties:dict):
        '''Method allows to change component properties
        component - component label, str
        properties - component properties, dict:
            molar_mass
            gamma
            Tb
            critical_pressure
            critical_temperature
            acentric_factor
            shift_parameter
            critical_volume
            bip
        
        Должна быть логика, что есть db по умолчанию, что передано в словаре - то заменяется в db, а остальное остается без изменений
        '''
        
        avalible_properties = ['molar_mass', 'gamma', 'Tb', 'critical_pressure', 'critical_temperature', 
                               'acentric_factor', 'shift_parameter', 'critical_volume', 'bip']
        
        for property in list(properties.keys()):
            if property not in avalible_properties:
                raise KeyError(f'Property {property} not in db!')
            else:
                self._composition_data[property][component] = properties[property]
                print(f'{property}')




    def show_composition_dataframes(self):

        '''Print composition, component properties and bips'''


        composition_df = pd.DataFrame.from_dict(self._composition, orient= 'index').to_markdown()

        ## Костыль чтобы убрать bips
        main_data_df = pd.DataFrame.from_dict({k: self._composition_data[k] for k in list(self._composition_data.keys())[:-1]}).to_markdown()


        bips_df = pd.DataFrame.from_dict(self._composition_data['bip']).to_markdown()
        

        print(composition_df)
        print('========')
        print(main_data_df)
        print('========')
        print(bips_df)



    @property
    def composition_df(self):
        return pd.DataFrame.from_dict(self._composition, orient= 'index')
    
    @property
    def composition_properties_df(self):
        return pd.DataFrame.from_dict({k: self._composition_data[k] for k in list(self._composition_data.keys())[:-1]})
    
    @property
    def composition_bips_df(self):
        return pd.DataFrame.from_dict(self._composition_data['bip'])



if __name__ == '__main__':
    comp = Composition({'C1': 0.15, 'C2':0.15, 'C3': 0.1, 'C6': 0.1, 'C8':0.1, 'C9':0.1, 'C10': 0.1, 'C11': 0.1, 'C16':0.1}, 
                       c6_plus_bips_correlation=None,
                       c6_plus_correlations={'critical_temperature': 'pedersen',
                        'critical_pressure' : 'rizari_daubert',
                        'acentric_factor': 'Edmister',
                        'critical_volume': 'hall_yarborough',
                        'k_watson': 'k_watson',
                        'shift_parameter': 'jhaveri_youngren'})
    
    comp.show_composition_dataframes()
    
    comp.edit_component_properties('C1', {'molar_mass': 0.95, 'critical_pressure': 500})

    

    comp.show_composition_dataframes()

