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
            self.k_values = self.phase_stability.k_values_vapour
            #print('Нужен расчет Рэшфорда райса')



    ### Методы ###

    # Метод расчета ур-ия Рэшфорда-Райса
    ## Не используется
    def rashford_rice_equation(self, f_v):
        sum_h_fv = []
        for component in self.zi.keys():
            sum_h_fv.append((self.zi[component] * (self.k_values[component] - 1)) / 
                            (1 + f_v * (self.k_values[component] - 1)))

            return sum(sum_h_fv)


    # Метод расчета производной ур-ия Рэшфорда-Райса
    ## Не используется
    def div_rashford_rice_equation(self, f_v):
        sum_dh_fv = []
        for component in self.zi.keys():
            sum_dh_fv.append((self.zi[component] * math.pow((self.k_values[component] - 1),2)) / 
                            (1 + f_v * (self.k_values[component]-1)) ** 2)

            return sum(sum_dh_fv)


    # Метод поиска Fv методом бисекции
    def find_solve_bisection_v3(self, max_iter=100, tol=1e-13):
        # Вычисляем безопасные границы для fvv
        k_min = min(self.k_values.values())
        k_max = max(self.k_values.values())
        
        # Избегаем деления на ноль при k=1
        if abs(k_min - 1) < 1e-10 or abs(k_max - 1) < 1e-10:
            raise ValueError("k_values contains values too close to 1.0, which can cause division by zero.")
        
        # Устанавливаем границы fv_min и fv_max
        fv_min = -1 / (k_max - 1) + 1e-10  # Избегаем деления на ноль
        fv_max = 1 / (1 - k_min) - 1e-10
        
        def compute_sum(fv):
            total = 0.0
            for component in self.k_values:
                k = self.k_values[component]
                denominator = 1 + fv * (k - 1)
                if abs(denominator) < 1e-10:  # Защита от деления на ноль
                    denominator = 1e-10 if denominator > 0 else -1e-10
                total += self.zi[component] * (k - 1) / denominator
            return total
        
        # Проверяем, что решение существует (функция меняет знак на границах)
        sum_min = compute_sum(fv_min)
        sum_max = compute_sum(fv_max)
        
        if sum_min * sum_max > 0:
            raise ValueError("No solution exists in the given interval (function does not cross zero).")
        
        # Метод бисекции
        for _ in range(max_iter):
            fvv = (fv_min + fv_max) / 2
            sum_mid = compute_sum(fvv)
            
            if abs(sum_mid) < tol:
                return fvv
            
            if sum_min * sum_mid < 0:
                fv_max = fvv
                sum_max = sum_mid
            else:
                fv_min = fvv
                sum_min = sum_mid
        
        return fvv  # Возвращаем последнее приближение, если не достигли tol


    # Метод расчета состава газа через найденное Fv
    def define_yi_v(self, fv):
        yi_v = {}
        for component in self.zi.keys():
            yi_v[component] = self.zi[component] * self.k_values[component] / ((fv * (self.k_values[component] - 1) + 1))
        

        return yi_v


    # Метод расчета состава жидкости через найденное Fv
    def define_xi_l(self, fv):
        xi_l = {}
        for component in self.zi.keys():
            xi_l[component] = self.zi[component] / ((fv * (self.k_values[component] - 1)) + 1)
        

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
    equilibrium = PhaseEquilibrium({'C1': 0.4, 'nC4':0.6}, 5, 40)
    print(equilibrium.k_values)

    print(equilibrium.find_solve_bisection_v3())

    print(equilibrium.define_xi_l(0.2146))
    print(equilibrium.define_yi_v(0.2146))

