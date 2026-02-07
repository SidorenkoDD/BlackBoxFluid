import math
import numpy as np

"""
Значения sigma_c, Z_c, psi для компонент природных систем до C5+ для уравнения Брусиловского
"""

COMPONENT_PARAMS_FOR_BRS_EOS = {
    "N2": [0.75001, 0.34626, 0.37182],
    "CO2": [0.75282, 0.31933, 0.74212],
    "H2S": [0.78524, 0.30418, 0.38203],
    "C1": [0.75630, 0.33294, 0.37447],
    "C2": [0.77698, 0.31274, 0.49550],
    "C3": [0.76974, 0.31508, 0.53248],
    "iC4": [0.78017, 0.30663, 0.63875],
    "nC4": [0.76921, 0.31232, 0.57594]
}


def evaluate_BRS_EOS_component_params(component: str, omega: float, eos_type: str=None, c5_plus_flag: bool=False):
    """
    Рассчитывает параметры sigma_c, Z_c, psi для компоненты для УРС Брусиловского по корреляции

    component: str - Название компонента (H2S, N2, C1, nC4 и т.д.)
    omega: float - Ацентрический фактор компонента
    eos_type: str or None - 'SRK' или 'PR', или None. Если указан 'SRK' или 'PR' - сводит УРС к указанному виду. По умолчанию - None
    c5_plus_flag: bool - флаг, указывающий принадлежит ли компонент группе C5+

    return:
    Список [sigma_c, Z_c, psi]
    """

    if eos_type is not None:
        if eos_type == 'SRK':
            sigma_c = 0.753307
            Z_c = 1.0 / 3.0
            psi = 0.48 + 1.57 * omega - 0.176 * math.pow(omega, 2)
            return [sigma_c, Z_c, psi]
        elif eos_type == 'PR':
            sigma_c = 0.7703944
            Z_c = 0.3074
            if omega <= 0.49:
                psi = 0.37464 + 1.54226 * omega - 0.26992 * math.pow(omega, 2)
            else:
                psi = 0.379642 + 1.48503 * omega - 0.164423 * math.pow(omega, 2) + 0.016666 * math.pow(omega, 3)
            return [sigma_c, Z_c, psi]
        else:
            raise TypeError(f'Неподдерживаемый тип УРС: {eos_type}')

    if component in COMPONENT_PARAMS_FOR_BRS_EOS:
        return COMPONENT_PARAMS_FOR_BRS_EOS[component]

    if c5_plus_flag:

        # Для компонент фракции C5+
        sigma_c = 0.75001
        Z_c = 0.3357 - 0.0294 * omega

        if omega < 0.4489:
            psi = 1.050 + 0.105 * omega + 0.482 * math.pow(omega, 2)
        else:
            psi = 0.429 + 1.004 * omega + 1.561 * math.pow(omega, 2)

    else:

        # Для компонент, не принадлежащих УВ компонентам природных смесей (любые иные, например меркаптаны и т.д.),
        # используются значения для уравнения Пенга-Робинсона (PR EoS)
        sigma_c = 0.7703944
        Z_c = 0.3074
        if omega <= 0.49:
            psi = 0.37464 + 1.54226 * omega - 0.26992 * math.pow(omega, 2)
        else:
            psi = 0.379642 + 1.48503 * omega - 0.164423 * math.pow(omega, 2) + 0.016666 * math.pow(omega, 3)

    return [sigma_c, Z_c, psi]


# Тестовая функция для векторных вычислений
# def evaluate_BRS_EOS_component_params_vector(
#         components_name: np.ndarray,
#         components_omega: np.ndarray,
#         components_c5_plus_flag: np.ndarray
# ):
#     """
#     Vectorized calculation of (Z_c, sigma_c, psi) per component.
#
#     Parameters
#     ----------
#     components_name : np.ndarray of str/object
#         Component names in the desired output order.
#     components_omega : np.ndarray of float
#         Acentric factors (omega) for each component (same shape as names).
#     components_c5_plus_flag : np.ndarray of int/bool
#         0 for light components, 1 for heavy components (same shape as names).
#     table : dict
#         Lookup table for light components: name -> [sigma_c, Z_c, psi].
#
#     Returns
#     -------
#     Z_c : np.ndarray
#     sigma_c : np.ndarray
#     psi : np.ndarray
#         Each has the same shape as inputs.
#     """
#     table = COMPONENT_PARAMS_FOR_BRS_EOS
#
#     names = np.asarray(components_name, dtype=object)
#     omega = np.asarray(components_omega, dtype=float)
#     heavy_flag = np.asarray(components_c5_plus_flag).astype(bool)
#
#     # output arrays
#     sigma_c = np.empty_like(omega, dtype=float)
#     Z_c = np.empty_like(omega, dtype=float)
#     psi = np.empty_like(omega, dtype=float)
#
#     # -----------------------
#     # Heavy components (flag == 0)
#     # -----------------------
#     if np.any(heavy_flag):
#         om_h = omega[heavy_flag]
#
#         sigma_c[heavy_flag] = 0.75001
#         Z_c[heavy_flag] = 0.3357 - 0.0294 * om_h
#
#         psi_h1 = 1.050 + 0.105 * om_h + 0.482 * (om_h ** 2)
#         psi_h2 = 0.429 + 1.004 * om_h + 1.561 * (om_h ** 2)
#         psi[heavy_flag] = np.where(om_h < 0.4489, psi_h1, psi_h2)
#
#     # -----------------------
#     # Light components (flag == 1)
#     #  - if in table: take from table
#     #  - else: compute by rule
#     # -----------------------
#     light_flag = ~heavy_flag
#     if np.any(light_flag):
#         names_l = names[light_flag]
#         om_l = omega[light_flag]
#
#         # vectorized membership check
#         in_table = np.isin(names_l, list(table.keys()))
#
#         # (A) from table
#         if np.any(in_table):
#             P = np.array([table[n] for n in names_l[in_table]], dtype=float)  # [sigma, Z, psi]
#             sigma_c[light_flag][in_table] = P[:, 0]
#             Z_c[light_flag][in_table] = P[:, 1]
#             psi[light_flag][in_table] = P[:, 2]
#
#         # (B) compute for missing light components
#         if np.any(~in_table):
#             om_m = om_l[~in_table]
#
#             sigma_c_l = np.full_like(om_m, 0.7703944, dtype=float)
#             Z_c_l = np.full_like(om_m, 0.3074, dtype=float)
#
#             psi_l1 = 0.37464 + 1.54226 * om_m - 0.26992 * (om_m ** 2)
#             psi_l2 = 0.379642 + 1.48503 * om_m - 0.164423 * (om_m ** 2) + 0.016666 * (om_m ** 3)
#             psi_l = np.where(om_m <= 0.49, psi_l1, psi_l2)
#
#             # аккуратно записываем обратно в исходные позиции
#             idx_light = np.flatnonzero(light_flag)
#             idx_missing = idx_light[~in_table]
#
#             sigma_c[idx_missing] = sigma_c_l
#             Z_c[idx_missing] = Z_c_l
#             psi[idx_missing] = psi_l
#
#         # NOTE: выше для "in_table" использовалась sigma_c[light][in_table] (это view-копия),
#         # поэтому для надежности аналогично запишем через индексы:
#         if np.any(in_table):
#             idx_light = np.flatnonzero(light_flag)
#             idx_table = idx_light[in_table]
#             sigma_c[idx_table] = np.array([table[n][0] for n in names_l[in_table]], dtype=float)
#             Z_c[idx_table] = np.array([table[n][1] for n in names_l[in_table]], dtype=float)
#             psi[idx_table] = np.array([table[n][2] for n in names_l[in_table]], dtype=float)
#
#     return sigma_c, Z_c, psi


"""
Значения коэффициентов парного взаимодействия для компонент природных систем C6+ для уравнения Брусиловского
"""

# Для некоторых пар компонент отсутствуют значения коэффициентов (см. комментарии)
BRS_EOS_CORRELATION_COEFS_FOR_BIPS = {
    'N2': {
        'N2': [0.0, 0.0, 0.0],
        'H2S': [-0.06, 2.06, 0.659],
        'CO2': [0.084, 0.76, 0.0],
        'C1': [0.03, 0.0, 0.0],
        'C2': [0.04, 0.0, 0.0],
        'C3': [0.131, 0.0, 0.0],
        'iC4': [-0.041, 1.081, 0.0],
        'nC4': [0.105, 0.771, 0.0],
        'iC5': [0.104, 1.202, 0.0],
        'nC5': [0.111, 1.048, 0.0]
    },
    'H2S': {
        'N2': [-0.06, 2.06, 0.659],
        'H2S': [0.0, 0.0, 0.0],
        'CO2': [0.012, 0.453, 0.0],
        'C1': [0.059, 0.089, 0.578],
        'C2': [0.07, -0.13, 0.0],
        'C3': [0.057, 0.0, 0.0],
        'iC4': [0.035, 0.225, 0.0],
        'nC4': [0.064, 0.116, 0.0],
        'nC5': [-0.023, 0.431, 0.442],
        'iC5': [-0.023, 0.431, 0.442]
        # В книге Брусиловского А. И. отсутствовали значения параметров для пары компонент H2S-iC5, поэтому для этой пары компонент приняты значения для пары H2S - nC5
    },
    'CO2': {
        'N2': [0.084, 0.76, 0.0],
        'H2S': [0.012, 0.453, 0.0],
        'CO2': [0.0, 0.0, 0.0],
        'C1': [0.127, 0.137, 0.0],
        'C2': [0.11, 0.0, 0.0],
        'C3': [0.08, 0.588, 0.0],
        'iC4': [0.054, 0.418, 0.0],
        'nC4': [0.095, 0.383, 0.0],
        'iC5': [0.108, 0.48, 0.0],
        'nC5': [0.098, 0.54, 0.0]
    },
    'C1': {
        'N2': [0.03, 0.0, 0.0],
        'H2S': [0.059, 0.089, 0.578],
        'CO2': [0.127, 0.137, 0.0],
        'C1': [0.0, 0.0, 0.0],
        'C2': [-0.015, 0.123, -0.41],
        'C3': [0.019, 0.502, 0.0],
        'iC4': [-0.065, 1.081, 0.0],
        'nC4': [0.031, 0.502, 0.0],
        'iC5': [0.001, 0.57, 0.0],
        'nC5': [0.001, 0.604, 0.0]
    },
    'C2': {
        'N2': [0.04, 0.0, 0.0],
        'H2S': [0.07, -0.13, 0.0],
        'CO2': [0.11, 0.0, 0.0],
        'C1': [-0.015, 0.123, -0.41],
        'C2': [0.0, 0.0, 0.0],
        'C3': [-0.015, 0.0, 0.0],
        'iC4': [-0.025, 0.302, 0.0],
        'nC4': [0.004, 0.05, 0.0],
        'nC5': [-0.077, 0.744, 0.0],
        'iC5': [-0.077, 0.744, 0.0]
        # В книге Брусиловского А. И. отсутствовали значения параметров для пары компонент С2-iC5, поэтому для этой пары компонент приняты значения для пары С2 - nC5
    },
    'C3': {
        'N2': [0.131, 0.0, 0.0],
        'H2S': [0.057, 0.0, 0.0],
        'CO2': [0.08, 0.588, 0.0],
        'C1': [0.019, 0.502, 0.0],
        'C2': [-0.015, 0.0, 0.0],
        'C3': [0.0, 0.0, 0.0],
        'iC4': [-0.063, 0.559, 0.0],
        # В книге Брусиловского А. И. отсутствовали значения параметров для пары компонент С3-iC4, поэтому для этой пары компонент приняты значения для пары С3 - nC4
        'nC4': [-0.063, 0.559, 0.0],
        'iC5': [-0.067, 0.844, 0.0],
        'nC5': [-0.074, 0.9, 0.0],
    },
    'iC4': {
        'N2': [-0.041, 1.081, 0.0],
        'H2S': [0.035, 0.225, 0.0],
        'CO2': [0.054, 0.418, 0.0],
        'C1': [-0.065, 1.081, 0.0],
        'C2': [-0.025, 0.302, 0.0],
        'C3': [-0.063, 0.559, 0.0],
        'iC4': [0.0, 0.0, 0.0],
        'nC4': [0.0, 0.0, 0.0],
        'iC5': [0.0, 0.0, 0.0],
        'nC5': [0.0, 0.0, 0.0],
    },
    'nC4': {
        'N2': [0.105, 0.771, 0.0],
        'H2S': [0.064, 0.116, 0.0],
        'CO2': [0.095, 0.383, 0.0],
        'C1': [0.031, 0.502, 0.0],
        'C2': [0.004, 0.05, 0.0],
        'C3': [-0.063, 0.559, 0.0],
        'iC4': [0.0, 0.0, 0.0],
        'nC4': [0.0, 0.0, 0.0],
        'iC5': [0.0, 0.0, 0.0],
        'nC5': [0.0, 0.0, 0.0]
    },
    'iC5': {
        'N2': [0.104, 1.202, 0.0],
        'H2S': [-0.023, 0.431, 0.442],
        'CO2': [0.108, 0.48, 0.0],
        'C1': [0.001, 0.57, 0.0],
        'C2': [-0.077, 0.744, 0.0],
        'C3': [-0.067, 0.844, 0.0],
        'iC4': [0.0, 0.0, 0.0],
        'nC4': [0.0, 0.0, 0.0],
        'iC5': [0.0, 0.0, 0.0],
        'nC5': [0.0, 0.0, 0.0]
    },
    'nC5': {
        'N2': [0.111, 1.048, 0.0],
        'H2S': [-0.023, 0.431, 0.442],
        'CO2': [0.098, 0.54, 0.0],
        'C1': [0.001, 0.604, 0.0],
        'C2': [-0.077, 0.744, 0.0],
        'C3': [-0.074, 0.9, 0.0],
        'iC4': [0.0, 0.0, 0.0],
        'nC4': [0.0, 0.0, 0.0],
        'iC5': [0.0, 0.0, 0.0],
        'nC5': [0.0, 0.0, 0.0]
    }
}


def get_coefs_for_BRS_EOS_bips_correlation_for_c5_plus(component: str, omega: float, Kw: float) -> list[float]:
    """
    Рассчитывает коэффициенты корреляции (e_ij, g_ij, h_ij) для коэффициентов парного взаимодействия легких компонент
    (N2, CO2, H2S, C1 - C3, iC4, nC4) с компонентами фракции C5+

    c_ij = e_ij + g_ij * t + h_ij * t^2, где t - температура в градусах Цельсия, С

    component: str - Название компонента, взаимодействующего с компонентом фракции C5+
    omega: float - Ацентрический фактор компонента фракции C5+
    Kw: float - Характеристический фактор Ватсона компонента фракции C5+

    return:
    Список трех чисел [e_ij, g_ij, h_ij]
    """

    if component == 'N2':
        return [0.138, 0.92 * math.pow(10, -3), 0.0]
    elif component == 'CO2':
        return [0.102, 0.30 * math.pow(10, -3), 0.0]
    elif component == 'H2S':
        return [-0.17 - 0.025 * omega, (0.99 - 2.24 * omega) * math.pow(10, -3),
                (0.43 + 0.054 * omega) * math.pow(10, -5)]
    elif component == 'C1':
        if Kw >= 12.4:
            return [-0.102 + 0.54 * omega - 0.53 * math.pow(omega, 2), (0.96 - 1.32 * omega) * math.pow(10, -3), 0.0]
        elif 10.6 <= Kw < 12.4:
            return [-0.102 + 0.54 * omega - 0.53 * math.pow(omega, 2), (0.75 - 1.54 * omega) * math.pow(10, -3), 0.0]
        else:
            return [-0.102 + 0.54 * omega - 0.53 * math.pow(omega, 2), (0.14 - 0.41 * omega) * math.pow(10, -3), 0.0]
    elif component == 'C2':
        return [-0.060, (1.15 - 1.61 * omega) * math.pow(10, -3), 0.0]
    elif component == 'C3':
        return [-0.071, 0.50 * math.pow(10, -3), 0.0]
    elif component in ('iC4', 'nC4'):
        return [0.0, 0.0, 0.0]
    else:
        return [0.0, 0.0, 0.0]


def evaluate_BRS_EOS_bip_for_c5_plus(component1: str, component2: str, T: float, omega: float, Kw: float):
    """
    Рассчитывает коэффициенты парного взаимодействия компонент фракции C5+ с остальными компонентами

    c_ij = e_ij + g_ij * t + h_ij * t^2, где t - температура в градусах Цельсия

    component1: str - Название компонента из фракции C5+ (C6, C7, C18 и т.д.)
    component2: str - Название второго компонента (N2, CO2, C6, C17 и т.д.)
    T: float - Температура в K
    omega: float - Ацентрический фактор компонента фракции C5+
    Kw: float - Характеристический фактор Ватсона компонента фракции C5+

    return:
    Коэффициент парного взаимодействия
    """

    e_ij, g_ij, h_ij = get_coefs_for_BRS_EOS_bips_correlation_for_c5_plus(component2, omega, Kw)

    t = T - 273.15
    c_ij = e_ij + g_ij * t + h_ij * math.pow(t, 2)

    return c_ij


def evaluate_BRS_EOS_bip_below_c5_plus(component1: str, component2: str, T: float):
    """
    Рассчитывает коэффициенты парного взаимодействия легких компонент (CO2, N2, H2S, C1, C2, C3, iC4, nC4, iC5, nC5)
    друг с другом

    c_ij = e_ij + g_ij * t + h_ij * t^2, где t - температура в градусах Цельсия

    component1: str - Название первого взаимодействующего компонента
    component2: str - Название второго взаимодействующего компонента
    T: float - Температура в K

    return: c_ij
    Коэффициент парного взаимодействия
    """
    e_ij, g_ij, h_ij = BRS_EOS_CORRELATION_COEFS_FOR_BIPS[component1][component2]
    t = T - 273.15

    c_ij = e_ij + g_ij * math.pow(10, -3) * t + h_ij * math.pow(10, -5) * math.pow(t, 2)

    return c_ij


# Тестовая функция для векторных вычислений
# def build_bip_matrix_BRS(
#     T_K: float,
#     components_name: np.ndarray,
#     components_omega: np.ndarray,
#     components_c5_plus_flag: np.ndarray,
#     Kw: np.ndarray
# ) -> np.ndarray:
#     """
#     Build NxN symmetric matrix of binary interaction coefficients C_ij for BRS EOS.
#
#     Rules:
#       - Heavy-heavy: C_ij = 0
#       - Diagonal:    C_ii = 0
#       - Light-light: use BIPS_FOR_BRS_EOS[li][lj] = [e,g,h] (symmetric)
#       - Heavy-light and light-heavy:
#             C_ij = e + g*t + h*t^2
#         where [e,g,h] determined by the given piecewise rules with:
#           * component2 = light component name (N2/CO2/H2S/C1/C2/C3/iC4/nC4/else)
#           * omega = omega of the HEAVY component in the pair
#           * Kw    = Kw of the HEAVY component (can be scalar or array per component)
#
#     Inputs
#     ------
#     T_K : float
#         Temperature in Kelvin.
#     components_name : (N,) array-like of str/object
#     components_omega : (N,) array-like of float
#     components_c5_plus_flag : (N,) array-like of {0,1}
#         0 = light, 1 = heavy
#     Kw : float or (N,) array-like
#         Watson characterization factor for each component (only used for heavy components vs C1).
#         If scalar, applied to all heavy components.
#     BIPS_FOR_BRS_EOS : dict
#         Nested dict for light-light pairs:
#             BIPS_FOR_BRS_EOS[a][b] == [e, g, h]
#
#     Returns
#     -------
#     C : (N,N) np.ndarray of float
#         Symmetric BIP matrix with zeros on diagonal.
#     """
#     names = np.asarray(components_name, dtype=object)
#     omega = np.asarray(components_omega, dtype=float)
#     heavy = np.asarray(components_c5_plus_flag).astype(bool)
#     N = names.size
#
#     # Kw handling: scalar or per-component
#     Kw_h = np.asarray(Kw, dtype=float)
#
#     # Temperature in Celsius
#     t = float(T_K) - 273.15
#
#     # Prepare coefficient matrices e,g,h (so you can also reuse them if needed)
#     E = np.zeros((N, N), dtype=float)
#     G = np.zeros((N, N), dtype=float)
#     H = np.zeros((N, N), dtype=float)
#
#     idx_light = np.flatnonzero(~heavy)
#     idx_heavy = np.flatnonzero(heavy)
#
#     # -------------------------
#     # 1) Light - Light from dict
#     # -------------------------
#     # Usually count of light components is small, so a simple double-loop is fine and still "vector-friendly"
#     # for the final math (E,G,H -> C).
#     for a_pos, i in enumerate(idx_light):
#         ci = names[i]
#         for j in idx_light[a_pos + 1:]:
#             cj = names[j]
#             e, g, h = BRS_EOS_CORRELATION_COEFS_FOR_BIPS[ci][cj]
#             E[i, j] = E[j, i] = float(e)
#             G[i, j] = G[j, i] = float(g) * 1e-3
#             H[i, j] = H[j, i] = float(h) * 1e-5
#
#     # ---------------------------------------------------
#     # 2) Heavy - Light via piecewise correlation (vectorized per light type)
#     #    Here component2 = LIGHT name, omega/Kw taken from HEAVY component.
#     # ---------------------------------------------------
#     if idx_heavy.size and idx_light.size:
#         om_h = omega[idx_heavy]
#         light_names = names[idx_light]
#
#         # We'll fill columns for each light component type separately (fast: only a few types).
#         def set_pair_for_light_name(light_name: str, e_vec, g_vec, h_vec):
#             """Write e,g,h for all heavy i vs all light j matching light_name (both symmetric directions)."""
#             mask_j = (light_names == light_name)
#             if not np.any(mask_j):
#                 return
#             j_idx = idx_light[mask_j]  # light indices with this name
#
#             # Fill all heavy i against each selected light j
#             # E[np.ix_(idx_heavy, j_idx)] expects (len(heavy), len(j_idx)) broadcasting.
#             E[np.ix_(idx_heavy, j_idx)] = e_vec[:, None]
#             G[np.ix_(idx_heavy, j_idx)] = g_vec[:, None]
#             H[np.ix_(idx_heavy, j_idx)] = h_vec[:, None]
#
#             # symmetric
#             E[np.ix_(j_idx, idx_heavy)] = e_vec[None, :]
#             G[np.ix_(j_idx, idx_heavy)] = g_vec[None, :]
#             H[np.ix_(j_idx, idx_heavy)] = h_vec[None, :]
#
#         # N2
#         e = np.full_like(om_h, 0.138, dtype=float)
#         g = np.full_like(om_h, 0.92e-3, dtype=float)
#         h = np.zeros_like(om_h, dtype=float)
#         set_pair_for_light_name("N2", e, g, h)
#
#         # CO2
#         e = np.full_like(om_h, 0.102, dtype=float)
#         g = np.full_like(om_h, 0.30e-3, dtype=float)
#         h = np.zeros_like(om_h, dtype=float)
#         set_pair_for_light_name("CO2", e, g, h)
#
#         # H2S (depends on omega of HEAVY)
#         e = -0.17 - 0.025 * om_h
#         g = (0.99 - 2.24 * om_h) * 1e-3
#         h = (0.43 + 0.054 * om_h) * 1e-5
#         set_pair_for_light_name("H2S", e, g, h)
#
#         # C1 (depends on omega and Kw of HEAVY, piecewise on Kw)
#         e = -0.102 + 0.54 * om_h - 0.53 * (om_h ** 2)
#         g1 = (0.96 - 1.32 * om_h) * 1e-3
#         g2 = (0.75 - 1.54 * om_h) * 1e-3
#         g3 = (0.14 - 0.41 * om_h) * 1e-3
#         g = np.where(Kw_h >= 12.4, g1, np.where(Kw_h >= 10.6, g2, g3))
#         h = np.zeros_like(om_h, dtype=float)
#         set_pair_for_light_name("C1", e, g, h)
#
#         # C2
#         e = np.full_like(om_h, -0.060, dtype=float)
#         g = (1.15 - 1.61 * om_h) * 1e-3
#         h = np.zeros_like(om_h, dtype=float)
#         set_pair_for_light_name("C2", e, g, h)
#
#         # C3
#         e = np.full_like(om_h, -0.071, dtype=float)
#         g = np.full_like(om_h, 0.50e-3, dtype=float)
#         h = np.zeros_like(om_h, dtype=float)
#         set_pair_for_light_name("C3", e, g, h)
#
#         # iC4 / nC4 -> zeros (already zero by default)
#         # else -> zeros (already zero)
#
#     # -------------------------
#     # 3) Build final C_ij matrix
#     # -------------------------
#     C = E + G * t + H * (t ** 2)
#
#     # Force zeros on diagonal
#     np.fill_diagonal(C, 0.0)
#
#     # Heavy-heavy already zero by construction (E/G/H not set there)
#     return C



if __name__ == '__main__':
    components_name = np.array(['CO2', 'C1', 'C2', 'C3', 'iC4', 'nC4', 'iC5', 'nC5', 'C6', 'C7',
                                'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17',
                                'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26',
                                'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35',
                                'C36'])
    components_molar_fraction = np.array([0.00215084, 0.28200996, 0.14906814, 0.1151349, 0.01428557,
                                          0.03721452, 0.01177459, 0.01130441, 0.01900741, 0.03082202,
                                          0.04150619, 0.03400326, 0.03087204, 0.02525985, 0.02140835,
                                          0.02061804, 0.01812707, 0.01338522, 0.01134442, 0.00953372,
                                          0.0094937, 0.0099939, 0.0066726, 0.00623243, 0.00585228,
                                          0.00495193, 0.00469183, 0.00408159, 0.00361141, 0.00342133,
                                          0.00300117, 0.00278108, 0.00240094, 0.00234091, 0.00212083,
                                          0.00195076, 0.0018007, 0.00170066, 0.02406939])
    components_p_crit = np.array([7.387, 4.604, 4.884, 4.246, 3.648,
                                  3.797, 3.389, 3.37, 3.104, 3.13366969,
                                  2.88457446, 2.64052778, 2.42321095, 2.24212297, 2.08704578,
                                  1.97039325, 1.86313451, 1.75864977, 1.66879595, 1.59104031,
                                  1.531296, 1.48106625, 1.428287, 1.37872425, 1.33696306,
                                  1.29743617, 1.26109858, 1.22331181, 1.1904596, 1.15913453,
                                  1.13004507, 1.1057614, 1.0858563, 1.06592191, 1.04730087,
                                  1.02926037, 1.01233025, 0.99534495, 0.97936275])
    components_t_crit = np.array([304.69, 190.6, 305.42, 369.79,
                                  408.09, 425.19, 460.39, 469.59,
                                  507.5, 542.42528445, 570.54899034, 598.10170458,
                                  622.20763641, 643.21167292, 663.63777999, 682.05238877,
                                  700.52976767, 718.83072584, 734.01297626, 749.40587865,
                                  760.71789505, 771.23558747, 782.42509968, 793.55711092,
                                  803.92677426, 814.25781185, 823.47759891, 832.28599384,
                                  841.43931709, 850.56431874, 858.58880717, 865.90744486,
                                  872.52998136, 880.21530976, 886.81576374, 893.40592962,
                                  898.91135085, 905.48210931, 910.96855949])
    components_omega = np.array([0.225, 0.013, 0.099, 0.152, 0.185,
                                 0.201, 0.227, 0.251, 0.252, 0.314414,
                                 0.34463054, 0.37909707, 0.41514357, 0.45095549, 0.48781929,
                                 0.52087726, 0.55563607, 0.59376079, 0.63029383, 0.66656796,
                                 0.69692941, 0.72504733, 0.75707076, 0.79001403, 0.82045099,
                                 0.85163148, 0.88224769, 0.91612256, 0.94848072, 0.98169634,
                                 1.01448126, 1.04388935, 1.06959137, 1.09709452, 1.12380161,
                                 1.15103631, 1.17753952, 1.2058872, 1.23355507])
    components_c5_plus_flag = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    components_k_watson = np.array([12.27, 11.96, 11.86, 11.82, 11.82, 11.84, 11.86, 11.85, 11.84,
                                    11.84, 11.87, 11.87, 11.89, 11.9, 11.92, 11.94, 11.94, 11.95,
                                    11.96, 11.99, 12., 12.01, 12.03, 12.04, 12.04, 12.04, 12.04,
                                    12.05, 12.06, 12.06, 12.07])

    print(np.where(components_name == 'C6'))
    print(components_molar_fraction[np.where(components_name == 'C6')])
