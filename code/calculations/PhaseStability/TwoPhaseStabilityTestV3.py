import numpy as np

from ..EOS.BrusilovskiyEOSV2 import BrusilovskiyEOS
from ..Composition.CompositionV2 import Composition
from ..Utils.Constants import (
    TOL_TWO_PHASE_STABILITY_CONVERGENCE,
    TOL_TWO_PHASE_STABILITY_CONVERGENCE_TRIVIAL_SOLUTION,
)
from ..Utils.Errors import StopIterationError


class TwoPhaseStabilityTest:
    def __init__(self, composition: Composition, p: float, t: float):
        self.p = float(p)
        self.t = float(t)

        self.stable = None
        self.k_values_liquid = None
        self.k_values_vapour = None
        self.k_values_for_flash = None

        self.S_l = None
        self.S_v = None

        self.convergence_l = False
        self.convergence_v = False
        self.convergence_trivial_solution_l = False
        self.convergence_trivial_solution_v = False

        self._composition = composition
        self.zi = composition.composition
        self.composition_data = composition.composition_data

        # Векторное внутреннее представление
        self._components = tuple(self.zi.keys())
        self._component_index = {comp: i for i, comp in enumerate(self._components)}
        self._nc = len(self._components)

        self._z_feed = np.fromiter(
            (self.zi[c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

        self._acentric_factor = np.fromiter(
            (self.composition_data['acentric_factor'][c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )
        self._critical_pressure = np.fromiter(
            (self.composition_data['critical_pressure'][c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )
        self._critical_temperature = np.fromiter(
            (self.composition_data['critical_temperature'][c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

        self._k_v_arr = None
        self._k_l_arr = None
        self._k_flash_arr = None

        self._yi_v_arr = None
        self._xi_l_arr = None

        self._mixture_fugacities_arr = None

        # Публичные dict-представления для совместимости
        self.yi_v = None
        self.xi_l = None

    # =====================================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =====================================================================================

    def _array_to_dict(self, arr: np.ndarray):
        return {comp: float(arr[i]) for i, comp in enumerate(self._components)}

    def _dict_to_array(self, data: dict):
        return np.fromiter(
            (data[c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

    @staticmethod
    def _safe_log_metric(arr: np.ndarray):
        return float(np.sum(np.log(arr) ** 2))

    # =====================================================================================
    # WILSON K-VALUES
    # =====================================================================================

    def _calc_k_values_wilson_array(self):
        return np.exp(
            5.37 * (1.0 + self._acentric_factor) * (1.0 - (self._critical_temperature / self.t))
        ) / (self.p / self._critical_pressure)

    # =====================================================================================
    # РАСЧЕТ ПРОБНЫХ СОСТАВОВ
    # =====================================================================================

    def _calc_Yi_v(self, k_values_vapour: np.ndarray):
        return self._z_feed * k_values_vapour

    def _calc_Xi_l(self, k_values_liquid: np.ndarray):
        return self._z_feed / k_values_liquid

    @staticmethod
    def _calc_S(arr: np.ndarray):
        return float(np.sum(arr))

    @staticmethod
    def _normalize_mole_fractions(arr: np.ndarray, S: float):
        return arr / S

    # =====================================================================================
    # Ri
    # =====================================================================================

    @staticmethod
    def _calc_ri_vapour(vapour_fugacities: np.ndarray, mixture_fugacities: np.ndarray, S_v: float):
        # ri = exp(ln f_mix - ln f_vapour) / S_v
        return np.exp(mixture_fugacities - vapour_fugacities) / S_v

    @staticmethod
    def _calc_ri_liquid(liquid_fugacities: np.ndarray, mixture_fugacities: np.ndarray, S_l: float):
        # ri = exp(ln f_liquid - ln f_mix) * S_l
        return np.exp(liquid_fugacities - mixture_fugacities) * S_l

    @staticmethod
    def _update_k_values(k_values_old: np.ndarray, ri: np.ndarray):
        return k_values_old * ri

    @staticmethod
    def _check_convergence(ri: np.ndarray) -> bool:
        sum_sq_ri = float(np.sum((ri - 1.0) ** 2))
        return sum_sq_ri < TOL_TWO_PHASE_STABILITY_CONVERGENCE

    @staticmethod
    def _check_trivial_solution(k_values: np.ndarray):
        return float(np.sum(np.log(k_values) ** 2)) < TOL_TWO_PHASE_STABILITY_CONVERGENCE_TRIVIAL_SOLUTION

    # =====================================================================================
    # ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ
    # =====================================================================================

    def _interpetate_stability_analysis(self):
        if (
            (self.convergence_trivial_solution_v and self.convergence_trivial_solution_l)
            or ((self.S_v <= 1.0) and self.convergence_trivial_solution_l)
            or (self.convergence_trivial_solution_v and (self.S_l <= 1.0))
            or ((self.S_v <= 1.0) and (self.S_l <= 1.0))
        ):
            self.stable = True
            self._k_flash_arr = None
            self.k_values_for_flash = None

        elif (self.S_v > 1.0) and self.convergence_trivial_solution_l:
            self.stable = False
            self._k_flash_arr = self._k_v_arr.copy()
            self.k_values_for_flash = self._array_to_dict(self._k_flash_arr)

        elif self.convergence_trivial_solution_v and (self.S_l > 1.0):
            self.stable = False
            self._k_flash_arr = self._k_l_arr.copy()
            self.k_values_for_flash = self._array_to_dict(self._k_flash_arr)

        elif (self.S_v > 1.0) and (self.S_l > 1.0):
            self.stable = False
            self._k_flash_arr = self._k_v_arr * self._k_l_arr
            self.k_values_for_flash = self._array_to_dict(self._k_flash_arr)

        elif (self.S_v > 1.0) and (self.S_l <= 1.0):
            self.stable = False
            self._k_flash_arr = self._k_v_arr.copy()
            self.k_values_for_flash = self._array_to_dict(self._k_flash_arr)

        else:
            self.stable = False
            self._k_flash_arr = self._k_l_arr.copy()
            self.k_values_for_flash = self._array_to_dict(self._k_flash_arr)

    # =====================================================================================
    # ОСНОВНОЙ РАСЧЕТ
    # =====================================================================================

    def calculate_phase_stability(self):
        initial_eos = BrusilovskiyEOS(composition=self._composition, p=self.p, t=self.t)
        initial_eos.calc_eos()
        self._mixture_fugacities_arr = initial_eos.fugacities.copy()

        k_init = self._calc_k_values_wilson_array()
        self._loop_vapour(k_init.copy())
        self._loop_liquid(k_init.copy())

        self._interpetate_stability_analysis()

    # =====================================================================================
    # ЦИКЛ ПО VAPOUR-ТЕСТУ
    # =====================================================================================

    def _loop_vapour(self, k_values: np.ndarray):
        i = 0
        self._k_v_arr = k_values.copy()
        self.k_values_vapour = self._array_to_dict(self._k_v_arr)

        while True:
            Yi_v = self._calc_Yi_v(self._k_v_arr)
            self.S_v = self._calc_S(Yi_v)
            self._yi_v_arr = self._normalize_mole_fractions(Yi_v, self.S_v)
            self.yi_v = self._array_to_dict(self._yi_v_arr)

            new_composition = self._composition.new_composition(self.yi_v)
            self.vapour_eos = BrusilovskiyEOS(composition=new_composition, p=self.p, t=self.t)
            self.vapour_eos.calc_eos()
            vapour_fugacities = self.vapour_eos.fugacities

            ri_v = self._calc_ri_vapour(
                vapour_fugacities=vapour_fugacities,
                mixture_fugacities=self._mixture_fugacities_arr,
                S_v=self.S_v,
            )

            if self._check_convergence(ri_v):
                self.convergence_v = True
                break

            self._k_v_arr = self._update_k_values(self._k_v_arr, ri_v)
            self.k_values_vapour = self._array_to_dict(self._k_v_arr)

            if self._check_trivial_solution(self._k_v_arr):
                self.convergence_trivial_solution_v = True
                break

            i += 1
            if i > 100000:
                raise StopIterationError('Число итераций теста стабильности превысило 100000')

    # =====================================================================================
    # ЦИКЛ ПО LIQUID-ТЕСТУ
    # =====================================================================================

    def _loop_liquid(self, k_values: np.ndarray):
        i = 0
        self._k_l_arr = k_values.copy()
        self.k_values_liquid = self._array_to_dict(self._k_l_arr)

        while True:
            Xi_l = self._calc_Xi_l(self._k_l_arr)
            self.S_l = self._calc_S(Xi_l)
            self._xi_l_arr = self._normalize_mole_fractions(Xi_l, self.S_l)
            self.xi_l = self._array_to_dict(self._xi_l_arr)

            new_composition = self._composition.new_composition(self.xi_l)
            self.liquid_eos = BrusilovskiyEOS(composition=new_composition, p=self.p, t=self.t)
            self.liquid_eos.calc_eos()
            liquid_fugacities = self.liquid_eos.fugacities

            ri_l = self._calc_ri_liquid(
                liquid_fugacities=liquid_fugacities,
                mixture_fugacities=self._mixture_fugacities_arr,
                S_l=self.S_l,
            )

            if self._check_convergence(ri_l):
                self.convergence_l = True
                break

            self._k_l_arr = self._update_k_values(self._k_l_arr, ri_l)
            self.k_values_liquid = self._array_to_dict(self._k_l_arr)

            if self._check_trivial_solution(self._k_l_arr):
                self.convergence_trivial_solution_l = True
                break

            i += 1
            if i > 100000:
                raise StopIterationError('Число итераций теста стабильности превысило 100000')

    # =====================================================================================
    # СВОЙСТВО ДЛЯ РАСЧЕТА ТОЧКИ НАСЫЩЕНИЯ
    # =====================================================================================

    @property
    def k_vals_for_sat_point_calculation(self):
        if (self.stable is None) or self.stable:
            return None

        if (self.S_v > 1.0) and (self.S_l > 1.0):
            if self.S_v > self.S_l:
                return self.k_values_vapour
            return self.k_values_liquid

        return self.k_values_for_flash