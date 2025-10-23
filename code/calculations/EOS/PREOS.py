from pathlib import Path
import sys
import math as math
import numpy as np
import pandas as pd

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))


from calculations.EOS.BaseEOS import EOS
from calculations.Composition.component import Component
from calculations.Composition.Composition import Composition2
from calculations.Utils.Constants import CONSTANT_R


class PREOS(EOS):
    def __init__(self, composition_dataframe: pd.DataFrame, bips, p, t):
        super().__init__(composition_dataframe, bips, p, t)
        self.composition_dataframe = composition_dataframe
        self.bips = bips
        self.p = p
        self.t = t
        self.mixed_A = None
        self._linear_mixed_B = None
        self.real_roots_eos = None
        self.choosen_eos_root = None
        self.fugacities_by_roots = None
        self.choosen_eos_root = None
        self.choosen_fugacities = None

    
    def _calc_a(self, component, omega_a = 0.45724) -> float:
        '''Caclulation of **a** parameter for EOS

        Args
        ---------
        * component - component for calculation parameter a
        * omega_a - constant 0.45724

        Return
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
                math.pow(CONSTANT_R, 2) * alpha / self.components_properties['critical_pressure'][component])

    def _calc_a_vectorized(self, omega_a=0.45724, add_to_df=True) -> pd.Series:
        '''Vectorized calculation of **a** parameter for EOS
        
        Args
        ---------
        * omega_a - constant 0.45724
        * add_to_df - if True, adds result as column to composition_dataframe
        
        Return
        --------
        Series with parameter **a** for each component
        '''
        df = self.composition_dataframe
        
        # Проверка наличия необходимых колонок
        required_cols = ['acentric_factor', 'critical_temperature', 'critical_pressure']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        acentric = df['acentric_factor']
        T_c = df['critical_temperature']
        P_c = df['critical_pressure']
        
        # Векторизованный расчет m с использованием np.where
        m = np.where(acentric > 0.49,
                    0.3796 + 1.485 * acentric - 0.1644 * acentric**2 + 0.01667 * acentric**3,
                    0.37464 + 1.54226 * acentric - 0.26992 * acentric**2)
        
        # Вычисляем alpha
        alpha = (1 + m * (1 - np.sqrt(self.t / T_c))) ** 2
        
        # Вычисляем параметр a
        a = omega_a * T_c**2 * CONSTANT_R**2 * alpha / P_c
        
        # Добавляем в датафрейм если требуется
        if add_to_df:
            self.composition_dataframe = self.composition_dataframe.copy()
            self.composition_dataframe['a_parameter'] = a
            
            # Опционально: можно также добавить промежуточные расчеты для отладки
            self.composition_dataframe['m_factor'] = m
            self.composition_dataframe['alpha_factor'] = alpha
        
        return a

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
        return (omega_b * CONSTANT_R * self.components_properties['critical_temperature'][component] /
                 self.components_properties['critical_pressure'][component])

    def _calc_b_vectorized(self, omega_b=0.0778, add_to_df=True) -> pd.Series:
        '''Vectorized calculation of **b** parameter for EOS
        
        Args
        ---------
        * omega_b - constant 0.0778
        * add_to_df - if True, adds result as column to composition_dataframe
        
        Return
        --------
        Series with parameter **b** for each component
        '''
        df = self.composition_dataframe
        
        # Проверка наличия необходимых колонок
        required_cols = ['critical_temperature', 'critical_pressure']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        T_c = df['critical_temperature']
        P_c = df['critical_pressure']
        
        # Вычисляем параметр b
        b = omega_b * CONSTANT_R * T_c / P_c
        
        # Добавляем в датафрейм если требуется
        if add_to_df:
            self.composition_dataframe = self.composition_dataframe.copy()
            self.composition_dataframe['b_parameter'] = b
        
        return b

    def _calc_A(self, component) -> float:
        '''Calculation of **A** parameter for EOS
        
        Parameters:
            ---------
                component - component for calculation parameter **A**

        Returns:
            ---------
                parameter **A** for component
        '''
        return self._calc_a(component) * self.p/math.pow((CONSTANT_R * self.t), 2)

    def _calc_A_vectorized(self, add_to_df=True) -> pd.Series:
        '''Vectorized calculation of **A** parameter for EOS
        
        Args
        ---------
        * add_to_df - if True, adds result as column to composition_dataframe
        
        Return
        --------
        Series with parameter **A** for each component
        '''
        df = self.composition_dataframe
        
        # Проверяем, есть ли уже рассчитанный параметр a в датафрейме
        if 'a_parameter' not in df.columns:
            # Если нет - рассчитываем его
            self._calc_a_vectorized(add_to_df=True)
        
        # Получаем параметр a из датафрейма
        a = df['a_parameter']
        
        # Вычисляем параметр A
        A = a * self.p / (CONSTANT_R * self.t) ** 2
        
        # Добавляем в датафрейм если требуется
        if add_to_df:
            self.composition_dataframe = self.composition_dataframe.copy()
            self.composition_dataframe['A_parameter'] = A
        
        return A

    def _calc_B(self, component) -> float:
        '''Calculation of **B** parameter for EOS
        
        Parameters:
            ---------
                component - component for calculation parameter **B**

        Returns:
            ---------
                parameter **B** for component
        '''
        return self._calc_b(component) * self.p/ (CONSTANT_R * self.t)

    def _calc_B_vectorized(self, add_to_df=True, ensure_b_calculated=True) -> pd.Series:
        '''Vectorized calculation of **B** parameter for EOS
        
        Args
        ---------
        * add_to_df - if True, adds result as column to composition_dataframe
        * ensure_b_calculated - if True, automatically calculates 'b' if missing
        
        Return
        --------
        Series with parameter **B** for each component
        '''
        df = self.composition_dataframe
        
        # Проверяем наличие параметра b
        if 'b_parameter' not in df.columns:
            if ensure_b_calculated:
                self._calc_b_vectorized(add_to_df=True)
            else:
                raise ValueError("Parameter 'b' not found in dataframe. Call _calc_b_vectorized first or set ensure_b_calculated=True")
        
        # Вычисляем параметр B
        B = df['b_parameter'] * self.p / (CONSTANT_R * self.t)
        
        # Добавляем в датафрейм если требуется
        if add_to_df:
            self.composition_dataframe = self.composition_dataframe.copy()
            self.composition_dataframe['B_parameter'] = B
        
        return B

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

    def _calc_mixed_A_vectorized(self) -> float:
        '''Optimized calculation of mixed **A** parameter for EOS'''
        
        # Проверяем наличие необходимых данных
        required_cols = ['mole_fraction', 'A_parameter']
        missing_cols = [col for col in required_cols if col not in self.composition_dataframe.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Получаем данные
        zi = self.composition_dataframe['mole_fraction']
        sqrt_A = np.sqrt(self.composition_dataframe['A_parameter'])
        
        # Создаем матрицы
        zi_matrix = np.outer(zi, zi)
        sqrt_A_matrix = np.outer(sqrt_A, sqrt_A)
        
        # Получаем BIPS матрицу
        if hasattr(self, 'bips') and self.bips is not None:
            # Выравниваем BIPS матрицу по компонентам в датафрейме
            components = self.composition_dataframe.index
            bip_matrix = 1 - self.bips.reindex(index=components, columns=components).fillna(0).values
        else:
            bip_matrix = np.zeros((len(zi), len(zi)))
        
        # Вычисляем результат
        result = np.sum(zi_matrix * sqrt_A_matrix * bip_matrix)
        return result

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
    
    def _calc_linear_mixed_B_vectorized(self, recalculate=False) -> float:
        '''Calculation of mixed **B** parameter for EOS with caching
        
        Args
        ------
        * recalculate - if True, forces recalculation even if cached
        
        Returns
        ------
            linear mixed parameter **B** 
        '''
        # Проверяем кэш
        if hasattr(self, '_linear_mixed_B_cache') and not recalculate:
            return self._linear_mixed_B_cache
        
        
        # Векторизованный расчет: sum(zi * Bi)
        df = self.composition_dataframe
        result = (df['mole_fraction'] * df['B_parameter']).sum()
        
        # Кэшируем результат
        self._linear_mixed_B = result
        return result

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

    def _calc_shift_parameter_vectorized(self) -> float:
        '''Calculation of shift parameter for EOS
        
        Returns
        ------
        shift parameter
        '''
        # Проверяем наличие необходимых данных
        required_cols = ['mole_fraction', 'shift_parameter']
        missing_cols = [col for col in required_cols if col not in self.composition_dataframe.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if 'b_parameter' not in self.composition_dataframe.columns:
            # Если b_parameter нет, рассчитываем его
            self._calc_b_vectorized(add_to_df=True)
        
        # Векторизованный расчет: sum(zi * shift_parameter * bi)
        df = self.composition_dataframe
        result = (df['mole_fraction'] * df['shift_parameter'] * df['b_parameter']).sum()
        return result


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

        self.real_roots_eos = [zk0, zk1, zk2]
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

    def _ensure_fugacity_parameters_calculated(self):
        """Убеждаемся, что все необходимые параметры для расчета летучести рассчитаны"""
        required_attrs = ['mixed_A', 'mixed_B']
        # for attr in required_attrs:
        #     if not hasattr(self, attr):
        #         self.calculate_mixed_parameters()
        
        required_cols = ['mole_fraction', 'A_parameter', 'b_parameter']
        missing_cols = [col for col in required_cols if col not in self.composition_dataframe.columns]
        if missing_cols:
            self.calculate_eos_parameters(['a', 'b', 'A', 'B'])

    def _calc_sum_zi_Ai_full_vectorized(self):
        """Полностью векторизованный расчет sum_zi_Ai для всех компонентов"""
        df = self.composition_dataframe
        z = df['mole_fraction'].values
        sqrt_A = np.sqrt(df['A_parameter'].values)
        
        # Матрица BIP
        if hasattr(self, 'bips') and self.bips is not None:
            # Убедимся, что BIPS матрица соответствует компонентам в датафрейме
            bip_matrix = 1 - self.bips.reindex(index=df.index, columns=df.index).fillna(0).values
        else:
            bip_matrix = np.ones((len(df), len(df)))
        
        # Создаем матрицу sqrt_A_i * sqrt_A_j
        sqrt_A_matrix = np.outer(sqrt_A, sqrt_A)
        
        # sum over j для каждого i: z_j * bip_ij * sqrt_A_i * sqrt_A_j
        sum_zi_Ai = np.sum(z * bip_matrix * sqrt_A_matrix, axis=1)
        
        return pd.Series(sum_zi_Ai, index=df.index)

    def _calc_pure_fugacity_optimized(self, df, eos_roots):
        """Оптимизированный расчет летучести для чистого компонента"""
        n_components = len(df)
        n_roots = len(eos_roots)
        
        # Создаем матрицу для результатов [components × roots]
        results = np.zeros((n_components, n_roots))
        
        for root_idx, root in enumerate(eos_roots):
            # Векторизованный расчет для всех компонентов одновременно
            term1 = root - 1
            term2 = -np.log(np.abs(root - self._linear_mixed_B))  # abs для избежания проблем с отрицательными значениями
            log_arg = (root + (np.sqrt(2) + 1) * self._linear_mixed_B) / (root - (np.sqrt(2) - 1) * self._linear_mixed_B)
            term3 = - (self.mixed_A / (2 * np.sqrt(2) * self._linear_mixed_B)) * np.log(np.abs(log_arg))
            
            ln_fi = term1 + term2 + term3
            # Заменяем недопустимые значения
            ln_fi = np.where(np.isfinite(ln_fi), ln_fi, 0.0)
            results[:, root_idx] = ln_fi
        
        return pd.DataFrame(results, 
                        index=df.index, 
                        columns=[f'root_{i}' for i in range(n_roots)])

    def _calc_fugacity_PR_full_vectorized(self, eos_roots=None) -> pd.DataFrame:
        '''Fully vectorized fugacity calculation for all components and roots
        
        Parameters
        ---------
            eos_roots - array of EOS roots for calculation (if None, uses self.real_roots_eos)
        
        Returns
        ------
            DataFrame with ln_fugacity for each component and each root
        '''
        if eos_roots is None:
            eos_roots = self.real_roots_eos
        
        df = self.composition_dataframe
        n_components = len(df)
        
        # Проверяем и рассчитываем необходимые параметры
        self._ensure_fugacity_parameters_calculated()
        
        # Для чистого компонента
        if n_components == 1:
            return self._calc_pure_fugacity_optimized(df, eos_roots)
        
        # Для смеси
        # Предварительно вычисляем сумму zi_Ai для всех компонентов
        sum_zi_Ai = self._calc_sum_zi_Ai_full_vectorized()
        
        # Создаем матрицу для результатов [components × roots]
        n_roots = len(eos_roots)
        results = np.zeros((n_components, n_roots))
        
        # Векторные вычисления для всех компонентов
        B_i = df['b_parameter'].values
        z_i = df['mole_fraction'].values
        
        for root_idx, root in enumerate(eos_roots):
            # Проверяем допустимость корня
            if not ((root - self._linear_mixed_B) > 0 and root > 0):
                continue  # оставляем нули для недопустимых корней
            
            # Векторизованный расчет для всех компонентов
            term1 = (B_i / self._linear_mixed_B) * (root - 1)
            term2 = -np.log(root - self._linear_mixed_B)
            
            log_arg_numerator = root + (1 + np.sqrt(2)) * self._linear_mixed_B
            log_arg_denominator = root + (1 - np.sqrt(2)) * self._linear_mixed_B
            log_ratio = log_arg_numerator / log_arg_denominator
            
            term3_coeff = (self.mixed_A / (2 * np.sqrt(2) * self._linear_mixed_B))
            term3_inner = (B_i / self._linear_mixed_B) - (2 / self.mixed_A) * sum_zi_Ai.values
            term3 = term3_coeff * term3_inner * np.log(log_ratio)
            
            ln_fi_i = term1 + term2 + term3
            ln_f_i = ln_fi_i + np.log(self.p * z_i)
            
            # Заменяем недопустимые значения (NaN, inf) на 0
            ln_f_i = np.where(np.isfinite(ln_f_i), ln_f_i, 0.0)
            results[:, root_idx] = ln_f_i
        
        return pd.DataFrame(results, 
                        index=df.index, 
                        columns=[f'root_{i}' for i in range(n_roots)])

    def _calc_fugacity_for_component_PR_vectorized(self, components=None, eos_roots=None) -> pd.DataFrame:
        '''Vectorized calculation of fugacity for specific components
        
        Parameters
        ---------
            components - list of components (if None, all components in dataframe)
            eos_roots - array of EOS roots for calculation
        
        Returns
        ------
            DataFrame with ln_fugacity for each specified component and each root
        '''
        if eos_roots is None:
            eos_roots = self.real_roots_eos
        
        if components is not None:
            df_subset = self.composition_dataframe.loc[components]
            # Пересчитываем mixed parameters для подмножества компонентов если нужно
            if len(components) == 1:
                # Для одного компонента используем полный расчет
                return self._calc_fugacity_PR_full_vectorized(eos_roots).loc[components]
            else:
                # Для подмножества компонентов пересчитываем sum_zi_Ai
                temp_df = self.composition_dataframe.copy()
                self.composition_dataframe = df_subset
                try:
                    result = self._calc_fugacity_PR_full_vectorized(eos_roots)
                finally:
                    self.composition_dataframe = temp_df
                return result
        else:
            return self._calc_fugacity_PR_full_vectorized(eos_roots)


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


    def calc_eos_vectorized(self):
        self._calc_a_vectorized()
        self._calc_b_vectorized()
        self._calc_A_vectorized()
        self._calc_B_vectorized()
        self.mixed_A = self._calc_mixed_A_vectorized()
        self.B_linear_mixed = self._calc_linear_mixed_B_vectorized()
        self.shift_parametr = self._calc_shift_parameter_vectorized()

        self._solve_cubic_equation()

        self.fugacities_by_roots = self._calc_fugacity_PR_full_vectorized()

        print(self.composition_dataframe)
        print(self.fugacities_by_roots)

    @property
    def z(self):
        return super().z()


    @property
    def fugacities(self):
        return super().fugacities()

    


if __name__ == '__main__':
    component_obj1 = Component('C1',0.9)
    component_obj6 = Component('C6',0.1)
    component_obj2 = Component('C9', 0.2)
    component_obj3 = Component('C13', 0.2)
    component_obj4 = Component('C14', 0.2)
    #composition_obj = Composition2([component_obj1, component_obj2, component_obj3, component_obj4, component_obj6])
    composition_obj2 = Composition2([component_obj1, component_obj6])
    

    eos = PREOS(composition_dataframe=composition_obj2._properties, bips = composition_obj2.bips, p = 10, t = 393.14)
    eos.calc_eos_vectorized()
    print(eos._solve_cubic_equation())
    print(eos._calc_fugacity_for_component_PR_vectorized())
