import math as math
from logger import LogManager
from PhaseStability_v2 import PhaseStability

class PhaseEquilibrium:
    '''
    Алгоритм

    1. Ввод zi, Р и Т
    2. Решаем УРС для состава zi
        2.1. Выбираем Z
        2.2. Расчет f
    3. Расчет начальные Кi
    4. Расчет yi_v и xi_l
    5. Решаем УРС для yi_v и xi_l
    6. Выбираем Zy и Zl
    7. Расчет f для каждой фазы
    8. Расчет Ri_v Ri_l
    9. Проверка сходимости -> Обновление Ki

    '''
    def __init__(self, zi : dict, p:float, t:float):
        self.zi = zi

        self.p = p * math.pow(10,5)
        self.t = t + 273


        self.phase_stability = PhaseStability(self.zi, self.p, self.t)



    ##TODO: FV не определено   
    def calc_xi(self, component, k_values):
        fv = 1
        xi = self.zi[component] / (1 + fv * (k_values['liquid'][component] - 1))
    

    # Метод расчета ур-ия Рэшфорда-Райса
    def rashford_rice_equation(self, k_values:dict, f_v):
        sum_h_fv = []
        for component in self.zi.keys():
            sum_h_fv.append((self.zi[component] * (k_values['vapour'][component] - 1)) / 
                            (1 + f_v * (k_values['vapour'][component] - 1)))


if __name__ == '__main__':
    equilibrium = PhaseEquilibrium({'C1': 0.1, 'C2':0.9}, 150,50)
    equilibrium.phase_stability.stability_analysis()
    equilibrium.phase_stability.interpretate_stability_analysis()