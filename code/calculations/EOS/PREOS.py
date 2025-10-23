from pathlib import Path
import sys
import math as math
import numpy as np
import time

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition


class PREOS(EOS):
    def __init__(self, zi, components_properties, p, t):
        super().__init__(zi, components_properties, p, t)
    
        self.zi = zi
        self.components_properties = components_properties
        self.p = p
        self.t = t

    
    def _calc_a(self, component, omega_a = 0.45724) -> float:
        '''Caclulation of **a** parameter for EOS

        Parameters:
            ---------
                component - component for calculation parameter a
                omega_a - constant 0.45724

        Returns:
            --------
                parameter **a** for component
        '''
        if self.components_properties['acentric_factor'][component] > 0.49:
            m = (0.3796 + 1.485 * self.components_properties['acentric_factor'][component]  - 
                 0.1644 * math.pow(self.components_properties['acentric_factor'][component],2) + 
                 0.01667 * math.pow(self.components_properties['acentric_factor'][component], 3))
        else:
            m = (0.37464 + 1.54226 * self.components_properties['acentric_factor'][component] - 
                 0.26992 * math.pow(self.components_properties['acentric_factor'][component], 2))

        alpha = math.pow(1 + m * (1 - math.sqrt(self.t/self.components_properties['critical_temperature'][component])), 2)
        
        return (omega_a * math.pow(self.components_properties['critical_temperature'][component],2) * 
                math.pow(8.31, 2) * alpha / self.components_properties['critical_pressure'][component])

    def _calc_b(self, component, omega_b = 0.0778) -> float:
        '''Calculation of **b** parameter for EOS
        Parameters:
            ---------
                component - component for calculation parameter **b**
                omega_a - constant 0.0778

        Returns:
            --------
                parameter **b** for component
        '''
        return (omega_b * 8.31 * self.components_properties['critical_temperature'][component] /
                 self.components_properties['critical_pressure'][component])

    def _calc_A(self, component) -> float:
        '''Calculation of **A** parameter for EOS
        
        Parameters:
            ---------
                component - component for calculation parameter **A**

        Returns:
            ---------
                parameter **A** for component
        '''
        return self._calc_a(component) * self.p/math.pow((8.31 * self.t), 2)

    def _calc_B(self, component) -> float:
        '''Calculation of **B** parameter for EOS
        
        Parameters:
            ---------
                component - component for calculation parameter **B**

        Returns:
            ---------
                parameter **B** for component
        '''
        return self._calc_b(component) * self.p/ (8.31 * self.t)

    def _calc_mixed_A_old(self) -> float:
        '''Calculation of mixed **A** parameter  for EOS
        
        Returns
            mixed parameter **A** 
        '''
        a_mixed = []
        second_components = list(self.zi.keys())
        for i_component in self.zi.keys():
            for j_component in second_components:
                a_mixed.append(self.zi[i_component] * self.zi[j_component] * math.sqrt(self.all_params_A[i_component] * self.all_params_A[j_component]) * (1 - self.components_properties['bip'][i_component][j_component]))

        return sum(a_mixed)

    def _calc_mixed_A(self) -> float:
        '''Calculation of mixed **A** parameter for EOS'''
        
        # Преобразуем данные в numpy arrays
        components = list(self.zi.keys())
        n = len(components)
        
        # Создаем векторы
        zi_vector = np.array([self.zi[comp] for comp in components])
        a_vector = np.array([self.all_params_A[comp] for comp in components])
        
        # Создаем матрицы взаимодействия
        zi_matrix = np.outer(zi_vector, zi_vector)  # zi_i * zi_j
        a_matrix = np.outer(a_vector, a_vector)     # a_i * a_j
        sqrt_a_matrix = np.sqrt(a_matrix)           # sqrt(a_i * a_j)
        
        # Матрица бинарных параметров взаимодействия
        bip_matrix = np.array([[1 - self.components_properties['bip'][i][j] 
                            for j in components] for i in components])
        
        # Вычисляем результат
        result_matrix = zi_matrix * sqrt_a_matrix * bip_matrix
        return np.sum(result_matrix)

    def _calc_linear_mixed_B(self) -> float:
        '''Calculation of mixed **B** parameter  for EOS
        
        Returns
        ------
            linear mixed parameter **B** 
        '''
        linear_mixed_B = []
        for i, b in enumerate(list(self.all_params_B.values())):
            linear_mixed_B.append(b * list(self.zi.values())[i])
        return sum(linear_mixed_B)

    def _calc_shift_parametr(self) -> float:
        '''Calculation of shift parameter  for EOS
        
        Returns
        ------
            shift parameter
        '''
        c_to_sum = []
        for component in self.zi.keys():
            # self.zi[component] * 
            c_to_sum.append(self.zi[component] * self.components_properties['shift_parameter'][component] * self.all_params_b[component])

        return sum(c_to_sum)

    def _solve_cubic_equation(self) -> list:
        '''Calculation of cubic equation
        
        Returns
        ------
            real eos roots -> list
        '''

        bk = self.B_linear_mixed - 1
        ck = self.mixed_A - 3 * (self.B_linear_mixed ** 2) - 2 * self.B_linear_mixed
        dk = (self.B_linear_mixed ** 2) + (self.B_linear_mixed ** 3) - self.mixed_A * self.B_linear_mixed
        pk = pk = -(bk ** 2) / 3 + ck
        qk = 2 * (bk ** 3) / 27 - (bk * ck/ 3 ) + dk
        s = ((pk/3) ** 3) + ((qk/2) ** 2) 

        if s > 0:
            vb = -qk/2 - (s ** (1/2)) 
            itt = -qk/2 + (s ** (1/2)) 
            if itt < 0:

                itt =  abs(itt)

                it =  (itt ** (1/3))
                it = - (itt ** (1/3))
            else:
                 it = itt ** (1/3)
            

            if vb < 0:
                    zk0 = it - ((abs(vb)) ** (1/3)) - bk/3
                
            else:
                    zk0 = it + ((-qk/2 - math.sqrt(s)) ** (1/3)) - bk/3

            zk1 = 0
            zk2 = 0
        
        elif s < 0:
            if qk < 0:
                f = math.atan(math.sqrt(-s) / (-qk/2))
            elif qk > 0:
                f = math.atan(math.sqrt(-s) / (-qk/2)) + math.pi
            else:
                f = math.pi / 2

            zk0 = 2 * math.sqrt(-pk/3) * math.cos(f/3) - bk/3
            zk1 = 2 * math.sqrt(-pk/3) * math.cos(f/3 + 2 * math.pi /3) - bk/3 
            zk2 = 2 * math.sqrt(-pk/3) * math.cos(f/3 + 4 * math.pi /3) - bk/3
        
        elif s == 0:
            zk0 = 2 * math.sqrt(-qk / 2) - bk/3
            zk1 = -math.pow((-qk/2), (1/3)) - bk/3
            zk2 = -math.pow((-qk/2), (1/3)) - bk/3


        return [zk0, zk1, zk2]

    def _calc_fugacity_for_component_PR(self, component, eos_root) -> float:
        '''Calculation of fugacity for component

        Parameters
        ---------
            component - component for calculation fugacity
            eos_root - eos root for calc

        Returns
        ------
            ln f_i for component
        '''
        if len(list(self.zi.keys())) == 1:
            eos_roots = self.real_roots_eos
            for root in eos_roots:
                ln_fi_i = (root - 1 - math.log(root - self.B_linear_mixed) - self.mixed_A / 
                           (2* math.sqrt(2) * self.B_linear_mixed) *  math.log((root + (math.sqrt(2) + 1) * 
                            self.B_linear_mixed)/(root - (math.sqrt(2) - 1) * self.B_linear_mixed)))
                return ln_fi_i
        else:
            zi_Ai = []
            for comp in list(self.zi.keys()):
                zi_Ai.append(self.zi[comp] * 
                                (1 - self.components_properties['bip'][component][comp]) * 
                                math.sqrt(self.all_params_A[component] * self.all_params_A[comp]))
            sum_zi_Ai = sum(zi_Ai)
            if ((eos_root - self.B_linear_mixed) > 0) and (eos_root > 0):
                ln_fi_i = ((self.all_params_B[component] / self.B_linear_mixed) * (eos_root - 1) -
                            (math.log(eos_root - self.B_linear_mixed)) + 
                            (self.mixed_A / (2 * math.sqrt(2) * self.B_linear_mixed)) * 
                            ((self.all_params_B[component] / self.B_linear_mixed) - (2/self.mixed_A) *  sum_zi_Ai) * 
                            math.log((eos_root + ((1 + math.sqrt(2))* self.B_linear_mixed)) / 
                                     (eos_root + ((1 - math.sqrt(2))* self.B_linear_mixed))))
                try:
                    ln_f_i = ln_fi_i + math.log(self.p * self.zi[component]) 
                    return ln_f_i
                except ValueError as e:
                   if "math domain error" in str(e):
                       return 0 
            else:
                return 0

    def _calc_fugacity_for_component_PR_numpy_vers(self, eos_root=None, component=None):
        # Кэшируем ключи и предвычисляем константы
        zi_keys = list(self.zi.keys())
        num_components = len(zi_keys)
        
        # Предварительно вычисленные константы для numpy
        sqrt2 = np.sqrt(2)
        sqrt2_plus_1 = sqrt2 + 1
        sqrt2_minus_1 = sqrt2 - 1
        
        if num_components == 1:
            # Векторизованная обработка корней с numpy
            eos_roots = np.array(self.real_roots_eos)
            B = self.B_linear_mixed
            A = self.mixed_A
            
            # Векторизованные вычисления для всех корней
            root_minus_B = eos_roots - B
            valid_roots_mask = root_minus_B > 0
            
            for i, root in enumerate(eos_roots):
                if not valid_roots_mask[i]:
                    continue
                    
                # Вычисляем числитель и знаменатель для логарифма
                numerator = root + sqrt2_plus_1 * B
                denominator = root - sqrt2_minus_1 * B
                
                if denominator <= 0:
                    continue
                    
                # Векторизованное вычисление логарифма
                log_term2 = np.log(numerator / denominator)
                
                ln_fi_i = (root - 1 - np.log(root - B) - 
                        A / (2 * sqrt2 * B) * log_term2)
                return ln_fi_i
            
        else:
            # Многокомпонентный случай
            if eos_root is None or component is None:
                return 0
                
            B = self.B_linear_mixed
            A = self.mixed_A
            
            # Проверка условий
            if (eos_root - B) <= 0 or eos_root <= 0:
                return 0
            
            # Векторизованное вычисление zi_Ai с numpy
            zi_Ai = []
            for comp in zi_keys:
                bip_val = self.components_properties['bip'][component][comp]
                sqrt_A = np.sqrt(self.all_params_A[component] * self.all_params_A[comp])
                zi_Ai.append(self.zi[comp] * (1 - bip_val) * sqrt_A)
            
            sum_zi_Ai = np.sum(zi_Ai)
            
            # Вычисление логарифмического члена
            numerator_log = eos_root + ((1 + sqrt2) * B)
            denominator_log = eos_root + ((1 - sqrt2) * B)
            
            if numerator_log <= 0 or denominator_log <= 0:
                return 0
                
            log_term = np.log(numerator_log / denominator_log)
            
            # Основное вычисление
            Bi_over_B = self.all_params_B[component] / B
            
            ln_fi_i = ((Bi_over_B * (eos_root - 1)) -
                    np.log(eos_root - B) + 
                    (A / (2 * sqrt2 * B)) * 
                    (Bi_over_B - (2 / A) * sum_zi_Ai) * log_term)
            
            # Финальное вычисление
            try:
                pressure_term = self.p * self.zi[component]
                if pressure_term > 0:
                    ln_f_i = ln_fi_i + np.log(pressure_term)
                    return ln_f_i
                else:
                    return 0
            except (ValueError, ArithmeticError):
                return 0
        
        return 0

    def _calc_normalized_gibbs_energy(self) -> dict:
        '''Calculation of normalized Gibbs energy. 
        
        Constraint for roots that less 0: returns 10^6 for Gibbs energy

        Returns
        ------
            normalized Gibbs energy for each root -> dict
        '''

        normalized_gibbs_energy = {}
        for root in self.fugacity_by_roots:
            gibbs_energy_by_roots = []
            if root <= 0:
                normalized_gibbs_energy[root] = math.pow(10,6)
            else:
                for component in self.fugacity_by_roots[root].keys():
                    gibbs_energy_by_roots.append(math.exp(self.fugacity_by_roots[root][component]) * self.zi[component])
                    normalized_gibbs_energy[root] = sum(gibbs_energy_by_roots)

        return normalized_gibbs_energy 

    def _choose_eos_root_by_gibbs_energy(self) -> float:
        '''Choosing EOS root by normalized Gibbs energy. 
        
        Returns
        ------
            Choosen EOS root
        '''
        min_gibbs_energy = min(self.normalized_gibbs_energy.values())
        return [k for k, v in self.normalized_gibbs_energy.items() if v == min_gibbs_energy][0]

    def calc_eos(self):
        '''Pipeline to calculate EOS

        '''
        
        self.all_params_a = {}
        self.all_params_b = {}
        for key in self.zi.keys():
            self.all_params_a[key] = self._calc_a(component=key)
            self.all_params_b[key] = self._calc_b(component=key)

        self.all_params_A = {}
        self.all_params_B = {}

        for key in self.zi.keys():
            self.all_params_A[key] = self._calc_A(component=key)
            self.all_params_B[key] = self._calc_B(component=key)

        self.mixed_A = self._calc_mixed_A()
        self.B_linear_mixed = self._calc_linear_mixed_B()
        self.shift_parametr = self._calc_shift_parametr()

        self.real_roots_eos = self._solve_cubic_equation()

        self.fugacity_by_roots = {}
        for root in [x for x in self.real_roots_eos if x != 0]:
            fugacity_by_components = {}
            for component in self.zi.keys():
                fugacity_by_components[component] = self._calc_fugacity_for_component_PR(component, root)
            self.fugacity_by_roots[root] = fugacity_by_components

        self.normalized_gibbs_energy = self._calc_normalized_gibbs_energy()
        self._z = self._choose_eos_root_by_gibbs_energy()
        self._fugacities = self.fugacity_by_roots[self._z]

        return None

    @property
    def z(self):
        return super().z()


    @property
    def fugacities(self):
        return super().fugacities()

    


if __name__ == '__main__':
    comp = Composition({'C6': 0.5, 'C7':0.5},
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'kesler_lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'Edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'})

    eos = PREOS(comp._composition,comp._composition_data, 10, 393.14)
    start_time = time.time()
    eos.calc_eos()
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.4f} секунд")
    print(f' Z: {eos.z}')
    print(f'fug_by_roots: {eos.fugacities}')
    print(f' Е Гиббса: {eos.normalized_gibbs_energy}')