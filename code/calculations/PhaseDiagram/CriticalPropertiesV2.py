import logging
import numpy as np

from ..EOS.BrusilovskiyEOSV2 import BrusilovskiyEOS
from ..Composition.CompositionV2 import Composition

log = logging.getLogger('MBALPVT.PVTDataModel.CritProps')


def _clip_mole_numbers(Y: np.ndarray, clip_min: float = 1e-30) -> np.ndarray:
    return np.maximum(Y, clip_min)


def _normalize_mole_numbers_to_fractions(Y: np.ndarray, clip_min: float = 1e-30) -> np.ndarray:
    Yc = _clip_mole_numbers(Y, clip_min)
    s = float(np.sum(Yc))
    if s <= 0.0:
        raise ValueError("Sum of trial mole numbers is non-positive after clipping.")
    return Yc / s


def modified_tangent_plane_criterion(
    Y: np.ndarray,
    z: np.ndarray,
    lnphi_Y: np.ndarray,
    lnphi_z: np.ndarray
):
    """
    Modified tangent plane criterion in vector form.
    """
    Yc = _clip_mole_numbers(Y)
    zc = _clip_mole_numbers(z)

    lnY = np.log(Yc)
    lnz = np.log(zc)

    g = lnY + lnphi_Y - lnz - lnphi_z
    F = 1.0 + float(np.sum(Yc * (lnY + lnphi_Y - lnz - lnphi_z - 1.0)))
    return F, g


class CriticalPointCalculator:
    def __init__(self, composition: Composition):
        self._composition = composition
        self.zi = composition.composition
        self.properties = composition.composition_data

        self._components = tuple(self.zi.keys())
        self._component_index = {c: i for i, c in enumerate(self._components)}
        self._nc = len(self._components)

        self._z = np.fromiter(
            (self.zi[c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

        self._pc = np.fromiter(
            (self.properties['critical_pressure'][c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

        self._tc = np.fromiter(
            (self.properties['critical_temperature'][c] for c in self._components),
            dtype=np.float64,
            count=self._nc,
        )

    # =====================================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =====================================================================================

    def _array_to_dict(self, arr: np.ndarray):
        return {c: float(arr[i]) for i, c in enumerate(self._components)}

    def _eos_lnphi_and_dlnphi_dx(self, T: float, P: float, x_arr: np.ndarray):
        """
        Возвращает:
            lnphi      : ndarray (N,)
            dlnphi_dx  : ndarray (N, N)

        Для выбранного корня EOS.
        """
        x_norm = _normalize_mole_numbers_to_fractions(x_arr)
        x_dict = self._array_to_dict(x_norm)

        new_composition = self._composition.new_composition(x_dict, deep_copy=True)
        if hasattr(new_composition, 'T'):
            new_composition.T = T

        eos = BrusilovskiyEOS(composition=new_composition, p=P, t=T)
        z_root, _ = eos.calc_eos()

        lnphi = eos.get_fugacity_coef_vector_by_root(z_root).copy()
        dlnphi_dx = eos._calc_dlogphi_dx_matrix().copy()

        return lnphi, dlnphi_dx

    # =====================================================================================
    # ОСНОВНЫЕ ВЫЧИСЛЕНИЯ b и c
    # =====================================================================================

    def _compute_b_c(self, T: float, P: float, eps: float = 1e-3):
        z = self._z
        N = self._nc

        lnphi_z, dlnphi_dx_z = self._eos_lnphi_and_dlnphi_dx(T, P, z)

        # d ln(phi_i) / d n_k
        # Векторизованная форма:
        # weighted_sum_i = sum_j x_j * dlnphi_dx[i,j]
        # dlnphi_dn[i,k] = dlnphi_dx[i,k] - weighted_sum_i
        # так как n_total = 1.0
        n_total = 1.0
        weighted_sum = dlnphi_dx_z @ z                      # shape (N,)
        dlnphi_dn_z = (dlnphi_dx_z - weighted_sum[:, None]) / n_total

        sqrtz = np.sqrt(z)
        B = np.eye(N, dtype=np.float64) + (sqrtz[:, None] * sqrtz[None, :]) * dlnphi_dn_z

        # Для симметризации как и в исходном коде
        Bsym = 0.5 * (B + B.T)

        evals, evecs = np.linalg.eigh(Bsym)
        idx = int(np.argmin(evals))
        lam_min = float(evals[idx])

        q = evecs[:, idx].astype(np.float64)
        q /= float(np.linalg.norm(q))

        b = 0.5 * lam_min

        # Trial mole numbers
        Y_plus = z + eps * q * sqrtz
        Y_minus = z - eps * q * sqrtz

        x_plus = _normalize_mole_numbers_to_fractions(Y_plus)
        x_minus = _normalize_mole_numbers_to_fractions(Y_minus)

        lnphi_plus, _ = self._eos_lnphi_and_dlnphi_dx(T, P, x_plus)
        lnphi_minus, _ = self._eos_lnphi_and_dlnphi_dx(T, P, x_minus)

        Fp, gp = modified_tangent_plane_criterion(Y_plus, z, lnphi_plus, lnphi_z)
        Fm, gm = modified_tangent_plane_criterion(Y_minus, z, lnphi_minus, lnphi_z)

        Fprime_plus = float(np.sum(sqrtz * q * gp))
        Fprime_minus = float(np.sum(sqrtz * q * gm))

        # Центральная разность
        c = (Fprime_plus + Fprime_minus) / (6.0 * eps * eps)

        return b, c

    # =====================================================================================
    # РЕШЕНИЕ СИСТЕМЫ ПО (T, P)
    # =====================================================================================

    def _solve_critical(
        self,
        T0: float,
        P0: float,
        tol: float = 1e-10,
        max_iter: int = 30,
        fd_T: float = 1e-2,
        fd_P: float = 1e-4,
        eps: float = 1e-3,
        damping: float = 1.0,
    ):
        T = float(T0)
        P = float(P0)

        for _ in range(max_iter):
            b0, c0 = self._compute_b_c(T, P, eps)

            if max(abs(b0), abs(c0)) < tol:
                return T, P

            dT = abs(fd_T)
            dP = abs(fd_P)

            b_Tp, c_Tp = self._compute_b_c(T + dT, P, eps)
            b_Tm, c_Tm = self._compute_b_c(T - dT, P, eps)
            b_Pp, c_Pp = self._compute_b_c(T, P + dP, eps)
            b_Pm, c_Pm = self._compute_b_c(T, P - dP, eps)

            db_dT = (b_Tp - b_Tm) / (2.0 * dT)
            dc_dT = (c_Tp - c_Tm) / (2.0 * dT)
            db_dP = (b_Pp - b_Pm) / (2.0 * dP)
            dc_dP = (c_Pp - c_Pm) / (2.0 * dP)

            J = np.array(
                [
                    [db_dT, db_dP],
                    [dc_dT, dc_dP],
                ],
                dtype=np.float64,
            )

            rhs = np.array([-b0, -c0], dtype=np.float64)

            try:
                step = np.linalg.solve(J, rhs)
            except np.linalg.LinAlgError as e:
                raise RuntimeError(f"Ошибка при решении СЛАУ в методе Ньютона: {e}")

            dT_step = float(step[0])
            dP_step = float(step[1])

            T = T + damping * dT_step
            P = P + damping * dP_step

        raise RuntimeError(f"Достигнуто максимальное число итераций: {max_iter}")

    # =====================================================================================
    # ПУБЛИЧНЫЙ МЕТОД
    # =====================================================================================

    def calculate(self, P0: float = None, T0: float = None):
        if P0 is None:
            pseudo_p = float(np.dot(self._z, self._pc))
            P0 = 2.0 * pseudo_p

        if T0 is None:
            pseudo_T = float(np.dot(self._z, self._tc))
            T0 = pseudo_T

        max_iter = 30
        damping = 1.0

        try:
            Tc, Pc = self._solve_critical(
                T0=T0,
                P0=P0,
                tol=1e-10,
                max_iter=max_iter,
                fd_T=1e-3,
                fd_P=1e-3,
                damping=damping,
                eps=1e-3,
            )
            return Tc, Pc
        except Exception as e:
            log.exception(e)
            max_iter = 100

        while damping > 0.01:
            try:
                Tc, Pc = self._solve_critical(
                    T0=T0,
                    P0=P0,
                    tol=1e-10,
                    max_iter=max_iter,
                    fd_T=1e-3,
                    fd_P=1e-3,
                    damping=damping,
                    eps=1e-3,
                )
                return Tc, Pc
            except Exception as e:
                log.exception(e)
                damping *= 0.9

        raise RuntimeError(
            'Метод не сошелся за макс. число итераций: 100, '
            'с минимальным параметром релаксации 0.01'
        )