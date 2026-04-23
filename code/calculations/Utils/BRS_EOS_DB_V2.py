import math
from calculations.Utils.Constants import CONSTANT_R

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


def _evaluate_params_for_SRK(omega: float):
    sigma_c = 0.753307
    Z_c = 1.0 / 3.0
    psi = 0.48 + 1.57 * omega - 0.176 * math.pow(omega, 2)
    return [sigma_c, Z_c, psi]


def _evaluate_params_for_PR(omega: float):
    sigma_c = 0.7703944
    Z_c = 0.3074
    if omega <= 0.49:
        psi = 0.37464 + 1.54226 * omega - 0.26992 * math.pow(omega, 2)
    else:
        psi = 0.379642 + 1.48503 * omega - 0.164423 * math.pow(omega, 2) + 0.016666 * math.pow(omega, 3)
    return [sigma_c, Z_c, psi]


def _evaluate_params_for_BRS_C5plus(omega: float):
    sigma_c = 0.75001
    Z_c = 0.3357 - 0.0294 * omega

    if omega < 0.4489:
        psi = 1.050 + 0.105 * omega + 0.482 * math.pow(omega, 2)
    else:
        psi = 0.429 + 1.004 * omega + 1.561 * math.pow(omega, 2)
    return [sigma_c, Z_c, psi]


def evaluate_BRS_EOS_component_params(component: str, omega: float, eos_name: str, c5_plus_flag: bool):
    """
    Рассчитывает параметры sigma_c, Z_c, psi для компоненты для УРС Брусиловского по корреляции

    component: str - Название компонента (H2S, N2, C1, nC4 и т.д.)
    omega: float - Ацентрический фактор компонента
    eos_type: str or None - 'SRK' или 'PR', или None. Если указан 'SRK' или 'PR' - сводит УРС к указанному виду. По умолчанию - None
    c5_plus_flag: bool - флаг, указывающий принадлежит ли компонент группе C5+

    return:
    Список [sigma_c, Z_c, psi]
    """

    if eos_name == 'SRKEOS':
        return _evaluate_params_for_SRK(omega)
    elif eos_name == 'PREOS':
        return _evaluate_params_for_PR(omega)
    elif eos_name == 'BRSEOS':
        if component in COMPONENT_PARAMS_FOR_BRS_EOS:
            return COMPONENT_PARAMS_FOR_BRS_EOS[component]

        if c5_plus_flag:
            # Для компонент фракции C5+
            return _evaluate_params_for_BRS_C5plus(omega)
        else:
            # Для компонент, не принадлежащих УВ компонентам природных смесей (любые иные, например меркаптаны и т.д.),
            # используются значения для уравнения Пенга-Робинсона (PR EoS)
            return _evaluate_params_for_PR(omega)
    else:
        raise RuntimeError(f'Неподдерживаемый тип УРС: {eos_name}')


def calc_alpha_beta_gamma_delta(OmegaC: float, Zc: float):

    alpha = math.pow(OmegaC, 3)
    beta = Zc + OmegaC - 1
    sigma = - Zc + OmegaC * (0.5 + math.pow(OmegaC - 0.75, 0.5))
    delta = - Zc + OmegaC * (0.5 - math.pow(OmegaC - 0.75, 0.5))

    return [alpha, beta, sigma, delta]


def calc_a_b_c_d(T: float, Pc: float, Tc: float, alpha: float, beta: float, sigma: float, delta: float, psi: float):

    phi = math.pow(1 + psi * (1 - math.pow(T / Tc, 0.5)), 2)
    a_c = alpha * math.pow(CONSTANT_R * Tc, 2) / Pc
    a = a_c * phi
    b = beta * CONSTANT_R * Tc / Pc
    c = sigma * CONSTANT_R * Tc / Pc
    d = delta * CONSTANT_R * Tc / Pc

    return [a, b, c, d]

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
        # 'C1': [0.059, 0.089, 0.578],
        'C1': [0.057, 0.435, 0.0],
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
        # 'H2S': [0.059, 0.089, 0.578],
        'H2S': [0.057, 0.435, 0.0],
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


def _get_coefs_for_BRS_EOS_bips_correlation_for_c5_plus(component: str, omega: float, Kw: float) -> list[float]:
    """
    Рассчитывает коэффициенты корреляции (e_ij, g_ij, h_ij) для коэффициентов парного взаимодействия легких компонент
    (N2, CO2, H2S, C1 - C3, iC4, nC4) с компонентами фракции C5+

    c_ij = e_ij + g_ij * t + h_ij * t^2, где t - температура в градусах Цельсия, С

    :param component: Название компонента, взаимодействующего с компонентом фракции C5+
    :param omega: Ацентрический фактор компонента фракции C5+
    :param Kw: Характеристический фактор Ватсона компонента фракции C5+

    :return: [e_ij, g_ij, h_ij]
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

    :param component1: Название компонента из фракции C5+ (C6, C7, C18 и т.д.)
    :param component2: Название второго компонента (N2, CO2, C6, C17 и т.д.)
    :param T: Температура в K
    :param omega: Ацентрический фактор компонента фракции C5+
    :param Kw: Характеристический фактор Ватсона компонента фракции C5+

    :return: Коэффициент парного взаимодействия + производная от коэффициента по T
    """

    e_ij, g_ij, h_ij = _get_coefs_for_BRS_EOS_bips_correlation_for_c5_plus(component2, omega, Kw)

    t = T - 273.15
    c_ij = e_ij + g_ij * t + h_ij * math.pow(t, 2)
    dc_ij_dT = g_ij + 2 * h_ij * t

    return c_ij, dc_ij_dT


def evaluate_BRS_EOS_bip_below_c5_plus(component1: str, component2: str, T: float):
    """
    Рассчитывает коэффициенты парного взаимодействия легких компонент (CO2, N2, H2S, C1, C2, C3, iC4, nC4, iC5, nC5)
    друг с другом

    c_ij = e_ij + g_ij * t + h_ij * t^2, где t - температура в градусах Цельсия

    :param component1: Название первого взаимодействующего компонента
    :param component2: Название второго взаимодействующего компонента
    :param T: Температура в K

    :return: c_ij - Коэффициент парного взаимодействия + производная от коэффициента по T
    """
    if component1 not in BRS_EOS_CORRELATION_COEFS_FOR_BIPS:
        return 0.0, 0.0

    if component2 not in BRS_EOS_CORRELATION_COEFS_FOR_BIPS:
        return 0.0, 0.0

    e_ij, g_ij, h_ij = BRS_EOS_CORRELATION_COEFS_FOR_BIPS[component1][component2]
    t = T - 273.15

    c_ij = e_ij + g_ij * math.pow(10, -3) * t + h_ij * math.pow(10, -5) * math.pow(t, 2)
    dc_ij_dT = g_ij * math.pow(10, -3) + 2 * h_ij * math.pow(10, -5) * t

    return c_ij, dc_ij_dT
