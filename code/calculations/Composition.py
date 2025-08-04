from PlusComponentProperties_v3 import PlusComponentProperties
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

        c6_plus_components = [int(item[1:]) for item in self.composition.keys() if int(item[1:]) > 6]
        self.c6_plus_components = c6_plus_components
        
    
    def _create_composition_db(self):
        with open(r'code/db/clear_components.json') as f:
            composition_data = json.load(f)

        if len(self.c6_plus_components) > 0:
            for component in self.c6_plus_components:
                cur_comp_properties = PlusComponentProperties('C'+str(component))
                cur_comp_properties.calculate_all_props_v2()

                composition_data['molar_mass']['C'+str(component)] = cur_comp_properties.data['M']
                composition_data['critical_pressure']['C'+str(component)] = cur_comp_properties.data['p_c']
                composition_data['critical_temperature']['C'+str(component)] = cur_comp_properties.data['t_c']
                composition_data['acentric_factor']['C'+str(component)] = cur_comp_properties.data['acentric_factor']


                print(cur_comp_properties)

        print(composition_data)







if __name__ == '__main__':
    comp = Composition({'C1': 0.25, 'C2':0.2, 'C5': 0.4, 'C15': 0.15})

    #print(comp.validate_c6_plus_components())

