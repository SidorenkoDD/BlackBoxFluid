import math as math
from scipy.optimize import newton, bisect
from logger import LogManager
from PhaseStability_v3 import PhaseStability


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

        if __name__ == '__main__':
            self.p = p 
            self.t = t + 273.14

        else:
            self.p = p
            self.t = t

        # Проводим анализ стабильности
        self.phase_stability = PhaseStability(self.zi, self.p, self.t)
        self.phase_stability.stability_loop()
        self.phase_stability.interpetate_stability_analysis()

        # 
        if self.phase_stability.stable == True:
            # Здесь переход к расчету свойств системы
            print('Сразу переходим к расчету свойств ')

        else:
            # Здесь переход к алгоритму Рэшфорда-Райса

            ##TODO: в каких случаях какие Кi берем в качестве исходных?
            self.k_values = self.phase_stability.k_values_liquid
            #print('Нужен расчет Рэшфорда райса')



    ### Методы ###

    # Метод расчета Fv_min
    def calc_fv_min(self):
        ...

    # Метод расчета Fv_max
    def calc_fv_max(self):
        ...
    


    # Метод расчета ур-ия Рэшфорда-Райса
    def rashford_rice_equation(self, f_v):
        sum_h_fv = []
        for component in self.zi.keys():
            sum_h_fv.append((self.zi[component] * (self.k_values[component] - 1)) / 
                            (1 + f_v * (self.k_values[component] - 1)))

            return sum(sum_h_fv)



    # Метод расчета производной ур-ия Рэшфорда-Райса
    def div_rashford_rice_equation(self, f_v):
        sum_dh_fv = []
        for component in self.zi.keys():
            sum_dh_fv.append((self.zi[component] * math.pow((self.k_values[component] - 1),2)) / 
                            (1 + f_v * (self.k_values[component]-1)) ** 2)

            return sum(sum_dh_fv)



    ## Метод для поиска решения Fv через алгоритм Ньютона
    def flash_newton(self):
        fv = newton(func = self.rashford_rice_equation,
                    x0 = 0.5, 
                    fprime= self.div_rashford_rice_equation, maxiter= 1000)

        return fv
    
    # Метод для поиска решения Fv через бисекцию
    def flash_bisect(self):
        fv = bisect(f = self.rashford_rice_equation,
                    a = -1, 
                    b = 1)
        print(fv)
        return fv

    # Метод расчета состава газа через Fv
    def define_yi_v(self, fv):
        yi_v = {}
        for component in self.zi.keys():
            yi_v[component] = self.zi[component] * self.k_values[component] / ((fv * self.k_values[component] - 1) + 1)
        
        print(yi_v)
        return yi_v

    # Метод расчета состава жидкости через Fv
    def define_xi_l(self, fv):
        xi_l = {}
        for component in self.zi.keys():
            xi_l[component] = self.zi[component] / ((fv * self.k_values[component] - 1) + 1)
        
        print(xi_l)
        return xi_l



    # Метод обновления Fv
    def update_fv(self):
        ...



    # Метод расчета шифт-параметра
    def clac_shift(self):
        ...



    # Метод расчета плотности системы
    def calc_rho(self):
        ...



if __name__ == '__main__':
    equilibrium = PhaseEquilibrium({'C1': 0.6, 'nC4':0.4}, 5, 40)
    print(equilibrium.k_values)
    equilibrium.flash_bisect()
    #equilibrium.define_yi_v(-4.42)
    #equilibrium.define_xi_l(-4.42)
