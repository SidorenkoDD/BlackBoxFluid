from PlusComponentProperties_v3 import PlusComponentProperties
import math
import json

class Composition:
    '''
        Класс для хранения и обработки состава флюида

        Methods:
        -------
        * validate_composition_sum - метод проверки суммы компонентов (граница по диапазону 0.999 <= sum_of_components <= 1)
        * validate_c7_plus_components - метод определяет, есть ли С6+ компоненты в исходном составе. Если да, то нужно производить
          дополнительный расчет свойств для тяжелых компонентов
        * create_composition_db - метод создает словарь, в котором будут храниться параметры компонент
    '''

    def __init__(self,  zi:dict):

        self.composition = zi
        self._validate_composition_sum()
        self._validate_c6_plus_components()
        self._create_composition_db()

    def _validate_composition_sum(self):
        sum_of_components = sum(self.composition.values())
        if not 0.999 <= sum_of_components <=1:
            raise ValueError('Сумма компонент не равна 1')



    def _validate_c6_plus_components(self):
        '''Метод определяет, есть ли С6+ компоненты в составе.
        Если есть, то рассчитывается и формируется единый словарь свойств для конкретного состава.
        '''

        c6_plus_components = [int(item[1:]) for item in self.composition.keys() if int(item[1:]) > 6]
        self.c6_plus_components = c6_plus_components
        
    
    def _create_composition_db(self):
        with open(r'code/db/clear_components.json') as f:
            self.composition_data = json.load(f)


        if len(self.c6_plus_components) > 0:



            for component in self.c6_plus_components:
                cur_comp_properties = PlusComponentProperties('C'+str(component))
                cur_comp_properties.calculate_all_props_v2()

                self.composition_data['molar_mass']['C'+str(component)] = cur_comp_properties.data['M']
                self.composition_data['critical_pressure']['C'+str(component)] = cur_comp_properties.data['p_c']
                self.composition_data['critical_temperature']['C'+str(component)] = cur_comp_properties.data['t_c']
                self.composition_data['acentric_factor']['C'+str(component)] = cur_comp_properties.data['acentric_factor']
                self.composition_data['critical_volume']['C'+str(component)] = cur_comp_properties.data['crit_vol']
                self.composition_data['shift_parametr']['C'+str(component)] = cur_comp_properties.data['Cpen']



    def _chueh_prausnitz_bip(self, component_i, component_j, A = 0.18, B = 6):

        v_ci = self.composition_data['critical_volume'][component_i]
        v_cj = self.composition_data['critical_volume'][component_j]

        return A * (1 - math.pow(((2 * math.pow(v_ci, 1/6) * math.pow(v_cj, 1/6))/(math.pow(v_ci, 1/3) + math.pow(v_cj, 1/3))), B))


    def _calculate_bips(self):
        if len(self.c6_plus_components) > 0:
            for component in self.composition.keys():
                
                for plus_component in self.c6_plus_components:
                    self.composition_data['bip'][component][plus_component] = self._chueh_prausnitz_bip(component_i=component, component_j= 'C' + str(plus_component))





if __name__ == '__main__':
    comp = Composition({'C1': 0.6, 'C15': 0.4})
    comp._calculate_bips()
    print(comp.composition_data['bip'])
    #print(comp.validate_c6_plus_components())

