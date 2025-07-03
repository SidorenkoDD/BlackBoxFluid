import math as math
from scipy.optimize import newton, bisect
from logger import LogManager
from EOS_PR_v2 import EOS_PR
from PhaseStability_v3 import PhaseStability
import yaml


class PhaseEquilibrium:
    '''

    '''

    def __init__(self, zi : dict, p:float, t:float, k_values):
        self.zi = zi

                # Подключение к yaml-файлику
        #try:
        with open('code/db.yaml', 'r') as db_file:
            self.db = yaml.safe_load(db_file)


        #except Exception as e:


        if __name__ == '__main__':
            self.p = p 
            self.t = t + 273.14

        else:
            self.p = p
            self.t = t

        self.k_values = k_values

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
    def find_solve_bisection_v4(self, tol=1e-13):
        fv_min = 0.0  # Минимально возможная доля пара
        fv_max = 1.0  # Максимально возможная доля пара

        def compute_sum(fvv):
            total = 0.0
            for component in self.k_values:
                K_i = self.k_values[component]
                z_i = self.zi[component]
                denominator = 1 + fvv * (K_i - 1)
                if abs(denominator) < 1e-10:
                    denominator = 1e-10  # Защита от деления на ноль
                total += z_i * (K_i - 1) / denominator
            return total

        # Проверяем, есть ли корень в [0, 1]
        sum_at_0 = compute_sum(0.0)
        sum_at_1 = compute_sum(1.0)

        if sum_at_0 * sum_at_1 > 0:
            raise ValueError("Нет решения в диапазоне fvv ∈ [0, 1]. Проверьте K_i и z_i.")

        # Метод бисекции
        for _ in range(100):
            fvv = (fv_min + fv_max) / 2
            sum_mid = compute_sum(fvv)

            if abs(sum_mid) < tol:
                return fvv

            if sum_at_0 * sum_mid < 0:
                fv_max = fvv
            else:
                fv_min = fvv

        return fvv
    

    # Метод расчета состава газа через найденное Fv
    def define_yi_v(self):
        yi_v = {}
        for component in self.zi.keys():
            yi_v[component] = round(self.zi[component] * self.k_values[component] / ((self.fv * (self.k_values[component] - 1) + 1)), 4)
        

        return yi_v


    # Метод расчета состава жидкости через найденное Fv
    def define_xi_l(self):
        xi_l = {}
        for component in self.zi.keys():
            xi_l[component] = round(self.zi[component] / ((self.fv * (self.k_values[component] - 1)) + 1), 4)
        

        return xi_l

    # Метод расчета Ri
    def calc_Ri(self, eos_vapour:EOS_PR, eos_liquid: EOS_PR):
        ri = {}
        for component in self.zi.keys():
            ri[component] = math.exp(eos_liquid.fugacity_by_roots[eos_liquid.choosen_eos_root][component]) / math.exp(eos_vapour.fugacity_by_roots[eos_vapour.choosen_eos_root][component]) 
        return ri


    # Метод проверки сходимости
    def check_convergence_ri(self, e = math.pow(10,-5)):
            
        ri_massive = []
        for ri in list(self.ri.values()):
            ri_massive.append((ri-1) ** 2)

        sum_ri = sum(ri_massive)

        if (sum_ri < e):
            self.convergence = True
            return True
        
        else:
            self.convergence = False
            return False
    
    
    # Метод обновления k_values
    def update_k_values(self):
        k_vals = {}
        for component in self.k_values.keys():
            k_vals[component] = self.k_values[component] * self.ri[component]
        
        return k_vals

    # Метод проверки тривиального решения
    def check_trivial_solution(self):
        ln_ki = []
        for component in self.k_values.keys():
            ln_ki.append(math.pow(math.log(self.k_values[component]), 2))
        
        if sum(ln_ki) < math.pow(10, -4):
            self.trivial_solution = True
            return True
        else:
            self.trivial_solution = False
            return False


    # Итерационный метод поиска решения
    def find_solve_loop(self):

        self.fv = self.find_solve_bisection_v4()

        # Определяем составы жидкой и газовой фазы
        self.yi_v = self.define_yi_v()
        self.xi_l = self.define_xi_l()

        # Создаем объекты УРС для решения газовой и жидкой фаз

        self.eos_vapour = EOS_PR(zi = self.yi_v, p = self.p, t = self.t)
        self.eos_liquid = EOS_PR(zi = self.xi_l, p = self.p, t = self.t)

        # Расчет Ri
        self.ri = self.calc_Ri(self.eos_vapour, self.eos_liquid)

        # Проверки сходимости
        self.check_convergence_ri()
        self.check_trivial_solution()
        

        while (self.convergence == False) and (self.trivial_solution == False):
            
            self.k_values = self.update_k_values()

            self.fv = self.find_solve_bisection_v4()

            self.yi_v = self.define_yi_v()
            self.xi_l = self.define_xi_l()

            self.eos_vapour = EOS_PR(zi = self.yi_v, p = self.p, t = self.t)
            self.eos_liquid = EOS_PR(zi = self.xi_l, p = self.p, t = self.t)

            self.ri = self.calc_Ri(self.eos_vapour, self.eos_liquid)

            self.check_convergence_ri()
            self.check_trivial_solution()



        return {'yi_v': self.yi_v,'xi_l':self.xi_l,  'Ki': self.k_values, 'Fv': self.fv, 'Z_v': self.eos_vapour.choosen_eos_root, 'Z_l': self.eos_liquid.choosen_eos_root}
