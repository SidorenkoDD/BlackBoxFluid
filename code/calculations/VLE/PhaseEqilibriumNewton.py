import math as math
import numpy as np
# from ..EOS.EOSFactory import EOSFactory
from ..EOS.BrusilovskiyEOS import BrusilovskiyEOS
from ..EOS.RootChooser import EOSRootChooser
from ..Composition.CompositionV2 import Composition
from ..Utils.Constants import TOL_TWO_PHASE_FLASH_CONVERGENCE, TOL_TWO_PHASE_FLASH_TRIVIAL_SOLUTION, TOL_TWO_PHASE_FLASH_BISECTION_CONVERGENCE
from src.tracer import trace_calls


class PhaseEquilibriumNewton:
    def __init__(self, composition: Composition, p: float, t: float, k_values):
        self.zi = composition.composition

        self._composition = composition
        # self._eos = EOSFactory().create_eos(eos)


        self._p = p
        self._t = t

        self.k_values = k_values
        self.L = 0.5
        self.fv = 1.0 - self.L

        self.xi_l = None
        self.yi_v = None
        self.ri = None
        self.eos_vapour = None
        self.eos_liquid = None

        self.convergence = False
        self.trivial_solution = False

    def find_solve_newton(self, fvv_init=None):
        fvv = self.fv if fvv_init is None else fvv_init

        k_min = min(list(self.k_values.values()))
        k_max = max(list(self.k_values.values()))

        if not ((k_min < 1) and (k_max > 1)):
            raise ValueError('Константы равновесия не удовлетворяют требованиям уравнения Рэчфорда-Райза')

        Fv_min = 1 / (1 - k_max)
        Fv_max = 1 / (1 - k_min)

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

        def compute_derivative(fvv):
            total = 0.0
            for component in self.k_values:
                K_i = self.k_values[component]
                z_i = self.zi[component]
                denominator = (1 + fvv * (K_i - 1)) ** 2
                if abs(denominator) < 1e-10:
                    denominator = 1e-10  # Защита от деления на ноль
                total -= (z_i * (K_i - 1) ** 2) / denominator
            return total

        residual1 = 1.0
        residual2 = 1.0
        i = 0
        while (residual1 > 1e-10) and (residual2 > 1e-10):
            # print(i)
            fvv_new = fvv - compute_sum(fvv) / compute_derivative(fvv)
            residual1 = abs(fvv_new - fvv)
            residual2 = abs(compute_sum(fvv_new))

            if Fv_min <= fvv_new <= Fv_max:
                fvv = fvv_new
            else:
                fvv = self.find_solve_bisection_v4(fvv)
                break

            i += 1

        # print(f'Количество итераций ур-я Р-Р (Newton): {i}; Корень: {fvv}')
        # print(f'Fv_min= {Fv_min}, Fv= {fvv}, Fv_max= {Fv_max}')
        return fvv

    def find_solve_bisection_v4(self, fvv_init=None):
        k_min = min(list(self.k_values.values()))
        k_max = max(list(self.k_values.values()))

        fv_min = 1 / (1 - k_max)
        fv_max = 1 / (1 - k_min)

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

        # Метод бисекции
        i = 0
        fvv = fvv_init if fvv_init is not None else 0.5 * (fv_min + fv_max)
        while True:
            sum_at_mid = compute_sum(fvv)

            if abs(sum_at_mid) < TOL_TWO_PHASE_FLASH_BISECTION_CONVERGENCE:
                return fvv

            sum_at_left = compute_sum(fv_min)

            if sum_at_left * sum_at_mid < 0:
                fv_max = fvv
            else:
                fv_min = fvv

            fvv = 0.5 * (fv_min + fv_max)

            i += 1
            if i > 1000:
                return fvv

    def fill_jacobian_fug_only(self):

        N_c = len(self.zi)

        J = np.zeros(shape=(N_c, N_c), dtype=np.float64)

        _dxi_dlnKi = {}
        _dyi_dlnKi = {}
        for comp in self.zi.keys():
            _dxi_dlnKi[comp], _dyi_dlnKi[comp] = self._calc_dxyi_dlnKi(comp)

        for i_row_1, component_row in enumerate(self.zi.keys()):

            for i_col_x, component_col in enumerate(self.zi.keys()):
                d_log_phi_l_i_dxk = self.eos_liquid.calc_d_log_phi_i_dxk(component_row, component_col)
                d_log_phi_v_i_dyk = self.eos_vapour.calc_d_log_phi_i_dxk(component_row, component_col)
                dxk_dlnKk = _dxi_dlnKi[component_col]
                dyk_dlnKk = _dyi_dlnKi[component_col]
                J[i_row_1][i_col_x] = d_log_phi_l_i_dxk * dxk_dlnKk - d_log_phi_v_i_dyk * dyk_dlnKk - float(i_row_1 == i_col_x)

        return J

    def fill_column_vector_fug_only(self):
        N_c = len(self.zi)

        b = [None] * N_c

        for i_1, component in enumerate(self.zi.keys()):

            ln_phi_l_i = self.eos_liquid.fugacity_coef_by_roots[self.eos_liquid.z][component]
            ln_phi_v_i = self.eos_vapour.fugacity_coef_by_roots[self.eos_vapour.z][component]
            ln_K_i = np.log(self.k_values[component])

            b[i_1] = ln_phi_l_i - ln_phi_v_i - ln_K_i

        b = np.array(b)

        return np.vstack(b)

    # @trace_calls(min_ms=0.02, max_depth=5, show_stdlib=False)
    def newton_algorithm_fug_only(self):
        k_i_arr = np.array(list(self.k_values.values()))
        log_k_i_arr = np.log(k_i_arr)

        jacobian = self.fill_jacobian_fug_only()
        b = self.fill_column_vector_fug_only()

        delta_vars = -np.linalg.solve(jacobian, b)
        delta_vars = delta_vars.T[0]

        log_k_i_arr_new = log_k_i_arr + delta_vars
        k_i_arr_new = np.exp(log_k_i_arr_new)

        k_vals = {}
        for i, component in enumerate(self.zi.keys()):
            k_vals[component] = k_i_arr_new[i]

        self.k_values = k_vals

    # @trace_calls(min_ms=1.0, max_depth=3, show_stdlib=False)
    def find_solve_loop(self):
        i = 0
        while True:

            self.fv = self.find_solve_newton()
            self.L = 1.0 - self.fv
            self.xi_l, self.yi_v = self.define_xi_l_yi_v()

            # Создаем объекты УРС для решения газовой и жидкой фаз
            vapour_composition = self._composition.new_composition(self.yi_v)
            self.eos_vapour = BrusilovskiyEOS(composition=vapour_composition, p=self._p, t=self._t)
            self.eos_vapour.calc_eos()
            # eos_root_chooser_vapour = EOSRootChooser(self.eos_vapour)
            # eos_root_chooser_vapour.define_root_for_phase('vapour')

            liquid_composition = self._composition.new_composition(self.xi_l)
            self.eos_liquid = BrusilovskiyEOS(composition=liquid_composition, p=self._p, t=self._t)
            self.eos_liquid.calc_eos()
            # eos_root_chooser_liquid = EOSRootChooser(self.eos_liquid)
            # eos_root_chooser_liquid.define_root_for_phase('liquid')

            self.ri = self.calc_Ri(self.eos_vapour, self.eos_liquid)

            self.check_convergence_ri()
            if self.convergence:
                break

            self.newton_algorithm_fug_only()

            self.check_trivial_solution()
            if self.trivial_solution:
                break

            i += 1

            if i > 1000:
                break

        return {'yi_v': self.yi_v, 'xi_l': self.xi_l, 'Ki': self.k_values, 'Fv': self.fv, 'Fl': self.L,
                'Z_v': self.eos_vapour.z, 'Z_l': self.eos_liquid.z}

    def _calc_dxyi_dlnKi(self, component_i):
        z_i = self.zi[component_i]
        x_i = self.xi_l[component_i]
        k_i = self.k_values[component_i]
        L = self.L
        dxi_dlnKi = - k_i * (x_i ** 2) * (1 - L) / z_i
        dyi_dlnKi = k_i * (x_i + dxi_dlnKi)
        return dxi_dlnKi, dyi_dlnKi

    # =====================================================================================

    def define_xi_l_yi_v(self):
        xi_l = {}
        yi_v = {}
        for component in self.zi.keys():
            L = self.L
            Ki = self.k_values[component]
            zi = self.zi[component]
            xi = zi / (L + (1.0 - L) * Ki)
            xi_l[component] = xi
            yi_v[component] = Ki * xi

        return xi_l, yi_v

    # Метод расчета Ri
    def calc_Ri(self, eos_vapour, eos_liquid):
        ri = {}
        for component in self.zi.keys():
            ri[component] = math.exp(eos_liquid.fugacities[component] - eos_vapour.fugacities[component])
        return ri

    # Метод проверки сходимости
    def check_convergence_ri(self, e=TOL_TWO_PHASE_FLASH_CONVERGENCE):
        ri_massive = np.array(list(self.ri.values()))
        ri_massive -= 1
        ri_massive **= 2
        sum_ri = ri_massive.sum()

        if sum_ri < e:
            self.convergence = True
            return True

        else:
            self.convergence = False
            return False

    # Метод проверки тривиального решения
    def check_trivial_solution(self):
        ki = np.array(list(self.k_values.values()))
        ln_ki = np.log(ki)
        ln_ki **= 2
        sum_ln_ki = ln_ki.sum()

        if sum_ln_ki < TOL_TWO_PHASE_FLASH_TRIVIAL_SOLUTION:
            self.trivial_solution = True
            return True
        else:
            self.trivial_solution = False
            return False