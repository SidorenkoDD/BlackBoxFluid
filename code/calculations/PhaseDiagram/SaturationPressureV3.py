import math
import numpy as np

from ..EOS.BrusilovskiyEOSV2 import BrusilovskiyEOS
from ..Composition.CompositionV2 import Composition


def norm_array(x: np.ndarray) -> np.ndarray:
    s = float(np.sum(x))
    return x / s


def Y_from_K_dew_array(z: np.ndarray, K: np.ndarray) -> np.ndarray:
    return z / K


def Y_from_K_bubble_array(z: np.ndarray, K: np.ndarray) -> np.ndarray:
    return z * K


def check_convergence_array(z: np.ndarray, Y: np.ndarray, R: np.ndarray) -> bool:
    """
    Аналог исходной функции, но на массивах.
    """
    flag1 = abs(1.0 - float(np.sum(Y))) < 1e-13

    ratio = Y / z
    # защита от log(1)/log(1) и других численных артефактов
    denom = np.log(ratio)
    numer = np.log(R)

    # valid = np.abs(denom) > 1e-30
    # if not np.any(valid):
    #     flag2 = True
    # else:
    #     metric = float(np.sum(numer[valid] / denom[valid]))
    #     flag2 = (metric ** 2) < 1e-8

    metric = float(np.sum(numer / denom))
    flag2 = (metric ** 2) < 1e-8

    return flag1 and flag2


def check_trivial_array(z: np.ndarray, Y: np.ndarray) -> bool:
    metric = float(np.sum(np.log(Y / z)))
    return (metric ** 2) < 1e-4


class SaturationPointCalculator:
    """
    Rigorous saturation pressure at fixed T using user-provided initial K-values.

    Parameters
    ----------
    composition : Composition

    Returns
    -------
    p_sat : float
    y_sat : dict
        Состав зарождающейся фазы при найденном давлении насыщения.
    """

    def __init__(self, composition: Composition):
        self._composition = composition
        self.zi = composition.composition
        self.comps = tuple(self.zi.keys())

        self._component_index = {c: i for i, c in enumerate(self.comps)}
        self._nc = len(self.comps)

        self._z_feed = np.fromiter(
            (self.zi[c] for c in self.comps),
            dtype=np.float64,
            count=self._nc,
        )

    # =====================================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =====================================================================================

    def _array_to_dict(self, arr: np.ndarray):
        return {c: float(arr[i]) for i, c in enumerate(self.comps)}

    def _dict_to_array(self, dct: dict):
        return np.fromiter(
            (dct[c] for c in self.comps),
            dtype=np.float64,
            count=self._nc,
        )

    # =====================================================================================
    # ОСНОВНОЙ РАСЧЕТ
    # =====================================================================================

    def calculate(self, T, p1, p2, K, sattype='dew', damp=0.6):
        """
        Parameters
        ----------
        T : float
            Temperature, K
        p1 : float
            Stable pressure (single-phase), upper bound
        p2 : float
            Unstable pressure (two-phase), lower bound
        K : dict
            Initial K-values
        sattype : str
            'dew' or 'bubble'
        damp : float
            Newton damping factor

        Returns
        -------
        tuple[float, dict]
            (saturation pressure, incipient phase composition)
        """
        K_arr = self._dict_to_array(K)

        if sattype == 'dew':
            Y = Y_from_K_dew_array(self._z_feed, K_arr)
        elif sattype == 'bubble':
            Y = Y_from_K_bubble_array(self._z_feed, K_arr)
        else:
            raise ValueError("sattype must be either 'dew' or 'bubble'")

        p_low = float(p2)
        p_high = float(p1)
        p = p_low

        i = 0
        while True:
            S = float(np.sum(Y))
            y = norm_array(Y)
            y_dict = self._array_to_dict(y)

            # EOS для исходной смеси z
            eos_z = BrusilovskiyEOS(composition=self._composition, p=p, t=T)
            z_z, _ = eos_z.calc_eos()
            ln_phi_z = eos_z.get_fugacity_coef_vector_by_root(z_z)

            # EOS для зарождающейся фазы y
            y_composition = self._composition.new_composition(y_dict)
            eos_y = BrusilovskiyEOS(composition=y_composition, p=p, t=T)
            z_y, _ = eos_y.calc_eos()
            ln_phi_y = eos_y.get_fugacity_coef_vector_by_root(z_y)

            # R_i = (z_i * phi_i(z)) / (y_i * phi_i(y)) / S
            # Работать можно в exp от разности логарифмов
            R = np.exp(
                np.log(self._z_feed) + ln_phi_z
                - np.log(y) - ln_phi_y
            ) / S
            Y_new = Y * R
            convergence = check_convergence_array(self._z_feed, Y_new, R)
            trivial = check_trivial_array(self._z_feed, Y_new)

            if convergence or trivial:
                return p, self._array_to_dict(norm_array(Y_new))

            # dQ/dp using vector d ln(phi)/dp
            # 1/p между фазами сокращается, как и в исходном коде
            dlnphi_z_dp = eos_z._calc_dlogphi_dp_vector()
            dlnphi_y_dp = eos_y._calc_dlogphi_dp_vector()

            dQdp = float(np.sum((Y * R) * (dlnphi_y_dp - dlnphi_z_dp)))

            Q = 1.0 - S

            if abs(dQdp) > 1e-20 and math.isfinite(dQdp):
                p_new = p - damp * Q / dQdp
            else:
                raise RuntimeError(
                    'Ошибка в методе Ньютона. Производная либо 0, либо inf'
                )

            # p_low = p_new
            p = p_new
            Y = Y_new

            i += 1
            if i > 10000:
                raise RuntimeError(
                    "Превышено макс. число итераций: 10000. Давление насыщения/конденсации не найдено"
                )