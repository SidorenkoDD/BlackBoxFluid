class Composition:

    def __init__(self,  zi:dict):
        '''
        Класс для хранения и обработки состава флюида
        '''
        self.composition = zi
        self.validate_composition()

    def validate_composition(self):
        sum_of_components = sum(self.composition.values())
        if not 0.999 <= sum_of_components <=1:
            raise ValueError('Сумма компонент не равна 1')