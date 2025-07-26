from PlusComponentProperties import PlusComponentProperties

class Composition:
    '''
        Класс для хранения и обработки состава флюида

        Methods:
        -------
        * validate_composition_sum - метод проверки суммы компонентов (граница по диапазону 0.999 <= sum_of_components <= 1)
        * validate_c7_plus_components - метод определяет, есть ли С6+ компоненты в исходном составе. Если да, то нужно производить
          дополнительный расчет свойств для тяжелых компонентов
        * 
    '''

    def __init__(self,  zi:dict):

        self.composition = zi
        self.validate_composition_sum()

    def validate_composition_sum(self):
        sum_of_components = sum(self.composition.values())
        if not 0.999 <= sum_of_components <=1:
            raise ValueError('Сумма компонент не равна 1')



    def validate_c6_plus_components(self):

        c6_plus_components = [int(item[1:]) for item in self.composition.keys() if int(item[1:]) > 6]
        self.c6_plus_components = c6_plus_components
        #return c6_plus_components
    
    def create_composition_db(self):
        if len(self.c6_plus_components) == 0:
            ...






if __name__ == '__main__':
    comp = Composition({'C1': 0.1, 'C2':0.2, 'C5': 0.4, 'C7': 0.15, 'C8': 0.15})
    print(comp.validate_c6_plus_components())
