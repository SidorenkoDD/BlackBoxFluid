import numpy as np

from ..EOS.BrusilovskiyEOSV2 import BrusilovskiyEOS
from ..Composition.CompositionV2 import Composition
from ..Utils.Constants import (
    TOL_TWO_PHASE_FLASH_CONVERGENCE,
    TOL_TWO_PHASE_FLASH_TRIVIAL_SOLUTION,
    TOL_TWO_PHASE_FLASH_BISECTION_CONVERGENCE,
)


class PhaseEquilibriumNewton:
    _RR_EPS = 1e-12
    _RR_NEWTON_TOL = 1e-10
    _RR_MAX_ITER = 1000

    def __init__(self, composition: Composition, p: float, t: float, k_values):
        self._composition = composition
        self._p = float(p)
        self._t = float(t)

        self.zi = composition.composition
        self.k_values = dict(k_values)

        self.L = 0.5
        self.fv = 1.0 - self.L

        self.xi_l = None
        self.yi_v = None
        self.ri = None

        self.eos_vapour = None
        self.eos_liquid = None

        self.convergence = False
        self.trivial_solution = False

        # Внутреннее векторное представление
        self._components = tuple(self.zi.keys())
        self._component_index = {comp: i for i, comp in enumerate(self._components)}
        self._nc = len(self._components)

        self._z_feed = np.fromiter(
            (self.zi[c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

        self._k = np.fromiter(
            (self.k_values[c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )
        self._log_k = np.log(self._k)

        self._xi_l_arr = None
        self._yi_v_arr = None
        self._ri_arr = None

    # =====================================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =====================================================================================

    def _array_to_dict(self, arr: np.ndarray):
        return {comp: float(arr[i]) for i, comp in enumerate(self._components)}

    def _sync_k_array_from_dict(self):
        self._k = np.fromiter(
            (self.k_values[c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )
        self._log_k = np.log(self._k)

    def _sync_k_dict_from_array(self):
        self.k_values = {comp: float(self._k[i]) for i, comp in enumerate(self._components)}

    @staticmethod
    def _safe_denominator(arr: np.ndarray, eps: float):
        out = arr.copy()
        mask = np.abs(out) < eps
        if np.any(mask):
            out[mask] = np.where(out[mask] >= 0.0, eps, -eps)
        return out

    # =====================================================================================
    # УРАВНЕНИЕ РЭЧФОРДА-РАЙЗА
    # =====================================================================================

    def _rr_bounds(self):
        k_min = float(np.min(self._k))
        k_max = float(np.max(self._k))

        if not ((k_min < 1.0) and (k_max > 1.0)):
            raise ValueError(
                "Константы равновесия не удовлетворяют требованиям уравнения Рэчфорда-Райза"
            )

        fv_min = 1.0 / (1.0 - k_max)
        fv_max = 1.0 / (1.0 - k_min)
        return fv_min, fv_max

    def _rr_sum(self, fv: float):
        km1 = self._k - 1.0
        denom = 1.0 + fv * km1
        denom = self._safe_denominator(denom, self._RR_EPS)
        return float(np.sum(self._z_feed * km1 / denom))

    def _rr_sum_and_derivative(self, fv: float):
        km1 = self._k - 1.0
        denom = 1.0 + fv * km1
        denom = self._safe_denominator(denom, self._RR_EPS)

        rr_sum = np.sum(self._z_feed * km1 / denom)
        rr_der = -np.sum(self._z_feed * (km1 ** 2) / (denom ** 2))
        return float(rr_sum), float(rr_der)

    def find_solve_newton(self):
        fv_left, fv_right = self._rr_bounds()
        fv = float(np.clip(self.fv, fv_left, fv_right))

        for _ in range(self._RR_MAX_ITER):
            rr_sum, rr_der = self._rr_sum_and_derivative(fv)

            if rr_sum > 0.0:
                fv_left = fv
            else:
                fv_right = fv

            if np.isfinite(rr_der) and abs(rr_der) > self._RR_EPS:
                fv_new = fv - rr_sum / rr_der
            else:
                fv_new = 0.5 * (fv_left + fv_right)

            if (not np.isfinite(fv_new)) or (fv_new <= fv_left) or (fv_new >= fv_right):
                fv_new = 0.5 * (fv_left + fv_right)

            residual_step = abs(fv_new - fv)
            residual_func = abs(self._rr_sum(fv_new))

            fv = fv_new

            if (residual_step <= self._RR_NEWTON_TOL) and (residual_func <= self._RR_NEWTON_TOL):
                return fv

        return fv

    def find_solve_bisection_v4(self, tol=TOL_TWO_PHASE_FLASH_BISECTION_CONVERGENCE):
        fv_left, fv_right = self._rr_bounds()
        f_left = self._rr_sum(fv_left)

        fv = 0.5 * (fv_left + fv_right)

        for _ in range(self._RR_MAX_ITER):
            fv = 0.5 * (fv_left + fv_right)
            f_mid = self._rr_sum(fv)

            if abs(f_mid) < tol or abs(fv_right - fv_left) < tol:
                return fv

            if f_left * f_mid < 0.0:
                fv_right = fv
            else:
                fv_left = fv
                f_left = f_mid

        return fv

    # =====================================================================================
    # ФАЗОВЫЕ СОСТАВЫ
    # =====================================================================================

    def define_xi_l_yi_v(self):
        denom = self.L + (1.0 - self.L) * self._k
        denom = self._safe_denominator(denom, self._RR_EPS)

        self._xi_l_arr = self._z_feed / denom
        self._yi_v_arr = self._k * self._xi_l_arr

        self.xi_l = self._array_to_dict(self._xi_l_arr)
        self.yi_v = self._array_to_dict(self._yi_v_arr)

        return self.xi_l, self.yi_v

    # =====================================================================================
    # НЬЮТОН ПО ФУГИТИВНОСТЯМ
    # =====================================================================================

    def fill_jacobian_fug_only(self):
        """
        J_ik = d ln(phi_i^L)/d ln(K_k) - d ln(phi_i^V)/d ln(K_k) - delta_ik

        d ln(phi_i)/d ln(K_k) = sum_j d ln(phi_i)/d x_j * d x_j/d ln(K_k)
        или аналогично для vapor-фазы.

        Здесь:
            dlogphi_dx_l = d ln(phi_i^L) / d x_j^L
            dlogphi_dx_v = d ln(phi_i^V) / d y_j^V
        берутся напрямую из:
            BrusilovskiyEOS._calc_dlogphi_dx_matrix()
        """
        # Матрицы производных ln(phi_i) по составам фаз
        dlogphi_dx_l = self.eos_liquid._calc_dlogphi_dx_matrix()   # shape (nc, nc)
        dlogphi_dx_v = self.eos_vapour._calc_dlogphi_dx_matrix()   # shape (nc, nc)

        z_safe = self._safe_denominator(self._z_feed, self._RR_EPS)

        # d x_k / d ln(K_k)
        dx_dlnk = -self._k * (self._xi_l_arr ** 2) * self.fv / z_safe   # shape (nc,)
        # d y_k / d ln(K_k)
        dy_dlnk = self._k * (self._xi_l_arr + dx_dlnk)                  # shape (nc,)

        # Цепное правило:
        # J_liq[i, k] = sum_j dlogphi_dx_l[i, j] * d x_j / d lnK_k
        # Но d x_j / d lnK_k = 0 при j != k, поэтому просто умножение столбцов
        j_liq = dlogphi_dx_l * dx_dlnk[None, :]
        j_vap = dlogphi_dx_v * dy_dlnk[None, :]

        J = j_liq - j_vap - np.eye(self._nc, dtype=np.float64)
        return J

    def fill_column_vector_fug_only(self):
        ln_phi_l = self.eos_liquid.get_fugacity_coef_vector_by_root(self.eos_liquid.z)
        ln_phi_v = self.eos_vapour.get_fugacity_coef_vector_by_root(self.eos_vapour.z)

        b = ln_phi_l - ln_phi_v - self._log_k
        return b.reshape(-1, 1)

    def newton_algorithm_fug_only(self):
        J = self.fill_jacobian_fug_only()
        b = self.fill_column_vector_fug_only()

        delta = -np.linalg.solve(J, b).ravel()

        self._log_k = self._log_k + delta
        self._k = np.exp(self._log_k)
        self._sync_k_dict_from_array()

    # =====================================================================================
    # Ri И КРИТЕРИИ ОСТАНОВКИ
    # =====================================================================================

    def calc_Ri(self, eos_vapour, eos_liquid):
        ln_f_l = eos_liquid.fugacities   # shape (nc,)
        ln_f_v = eos_vapour.fugacities   # shape (nc,)

        self._ri_arr = np.exp(ln_f_l - ln_f_v)
        self.ri = self._array_to_dict(self._ri_arr)
        return self.ri

    def check_convergence_ri(self, e=TOL_TWO_PHASE_FLASH_CONVERGENCE):
        sum_ri = float(np.sum((self._ri_arr - 1.0) ** 2))

        if sum_ri < e:
            self.convergence = True
            return True

        self.convergence = False
        return False

    def check_trivial_solution(self):
        trivial_metric = float(np.sum(self._log_k ** 2))

        if trivial_metric < TOL_TWO_PHASE_FLASH_TRIVIAL_SOLUTION:
            self.trivial_solution = True
            return True

        self.trivial_solution = False
        return False

    # =====================================================================================
    # ОСНОВНОЙ ЦИКЛ
    # =====================================================================================

    def find_solve_loop(self):
        i = 0

        while True:
            self.fv = self.find_solve_newton()
            self.L = 1.0 - self.fv

            self.define_xi_l_yi_v()

            vapour_composition = self._composition.new_composition(self.yi_v)
            self.eos_vapour = BrusilovskiyEOS(
                composition=vapour_composition,
                p=self._p,
                t=self._t,
            )
            self.eos_vapour.calc_eos()

            liquid_composition = self._composition.new_composition(self.xi_l)
            self.eos_liquid = BrusilovskiyEOS(
                composition=liquid_composition,
                p=self._p,
                t=self._t,
            )
            self.eos_liquid.calc_eos()

            self.calc_Ri(self.eos_vapour, self.eos_liquid)

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

        return {
            "yi_v": self.yi_v,
            "xi_l": self.xi_l,
            "Ki": self.k_values,
            "Fv": self.fv,
            "Fl": self.L,
            "Z_v": self.eos_vapour.z,
            "Z_l": self.eos_liquid.z,
        }