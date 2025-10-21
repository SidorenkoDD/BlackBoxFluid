import math as math
from calculations.EOS.BaseEOS import EOS
from calculations.EOS.EOSFactory import EOSFactory
from calculations.EOS.RootChooser import EOSRootChooser
from calculations.Composition.Composition import Composition
from calculations.Utils.Constants import TOL_TWO_PHASE_FLASH_CONVERGENCE, TOL_TWO_PHASE_FLASH_BISECTION_CONVERGENCE, TOL_TWO_PHASE_FLASH_TRIVIAL_SOLUTION



class PhaseEquilibrium:
    '''

    '''

    def __init__(self, composition: Composition, p:float, t:float, k_values, eos: str | EOS):
        self.zi = composition._composition
        self.db = composition._composition_data
        self.eos = EOSFactory().create_eos(eos)
        
        self.p = p
        self.t = t


        self.k_values = k_values

    ### Методы ###

    # Метод расчета ур-ия Рэшфорда-Райса

    def find_solve_bisection_v4(self, tol = TOL_TWO_PHASE_FLASH_BISECTION_CONVERGENCE):
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
        for _ in range(1000):
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
            yi_v[component] = self.zi[component] * self.k_values[component] / ((self.fv * (self.k_values[component] - 1) + 1))
        

        return yi_v


    # Метод расчета состава жидкости через найденное Fv
    def define_xi_l(self):
        xi_l = {}
        for component in self.zi.keys():
            xi_l[component] = self.zi[component] / ((self.fv * (self.k_values[component] - 1)) + 1)
        

        return xi_l

    # Метод расчета Ri
    def calc_Ri(self, eos_vapour, eos_liquid):
        ri = {}
        for component in self.zi.keys():
            ri[component] = math.exp(eos_liquid.fugacities[component]) / math.exp(eos_vapour.fugacities[component]) 
        return ri


    # Метод проверки сходимости
    def check_convergence_ri(self, e = TOL_TWO_PHASE_FLASH_CONVERGENCE):
    
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
        
        if sum(ln_ki) < TOL_TWO_PHASE_FLASH_TRIVIAL_SOLUTION:
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

        self.eos_vapour = self.eos(zi= self.yi_v, components_properties= self.db, p = self.p, t = self.t)
        self.eos_vapour.calc_eos()
        self.eos_root_chooser = EOSRootChooser(self.eos_vapour)
        self.eos_root_chooser.define_root_for_phase('vapour')
        

        self.eos_liquid = self.eos(zi = self.xi_l, components_properties= self.db, p = self.p, t = self.t)
        self.eos_liquid.calc_eos()
        self.eos_root_chooser = EOSRootChooser(self.eos_liquid)
        self.eos_root_chooser.define_root_for_phase('liquid')
        
        
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

            
            self.eos_vapour = self.eos(zi= self.yi_v, components_properties= self.db, p = self.p, t = self.t)
            self.eos_vapour.calc_eos()
            self.eos_root_chooser = EOSRootChooser(self.eos_vapour)
            self.eos_root_chooser.define_root_for_phase('vapour')

            self.eos_liquid = self.eos(zi= self.xi_l, components_properties= self.db, p = self.p, t = self.t)
            self.eos_liquid.calc_eos()
            self.eos_root_chooser = EOSRootChooser(self.eos_liquid)
            self.eos_root_chooser.define_root_for_phase('liquid')
            

            self.ri = self.calc_Ri(self.eos_vapour, self.eos_liquid)

            self.check_convergence_ri()
            self.check_trivial_solution()



        return {'yi_v': self.yi_v,'xi_l':self.xi_l,  'Ki': self.k_values, 'Fv': self.fv, 'Z_v': self.eos_vapour._z, 'Z_l': self.eos_liquid._z}
