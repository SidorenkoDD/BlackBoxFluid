import math
from typing import Dict, Callable
from calculations.Utils.Constants import CONSTANT_R


class CriticalTemperatureCorrelation:
    """
    Класс, содержащий корреляции для расчета критической температуры
    """

    @staticmethod
    def _roess(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Роесса (Roess, 1936)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическая температура в K
        """
        Tb_F = Tb_K * 9 / 5 - 459.67
        Tc_R = 645.83 + 1.6667 * (gamma * (Tb_F + 100)) - 0.727e-3 * math.pow(gamma * (Tb_F + 100), 2)
        return Tc_R * 5 / 9

    @staticmethod
    def _nokey(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Нокея (Nokey, 1959)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическая температура в K
        """
        Tb_R = Tb_K * 9 / 5
        Tc_R = 19.07871 * math.pow(Tb_R, 0.62164) * math.pow(gamma, 0.2985)
        return Tc_R * 5 / 9

    @staticmethod
    def _cavett(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Каветта (Cavett, 1962)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K
        :return: Критическая температура в K
        """
        gamma_api = 141.5 / gamma - 131.5
        Tb_F = Tb_K * 9 / 5 - 459.67
        Tc_R = (768.07121 + 1.7133693 * Tb_F - 0.10834003 * 1e-2 * math.pow(Tb_F, 2) -
                0.89212579 * 1e-2 * Tb_F * gamma_api +
                0.38890584 * 1e-6 * math.pow(Tb_F, 3) +
                0.5309492 * 1e-5 * math.pow(Tb_F, 2) * gamma_api +
                0.327116 * 1e-7 * math.pow(Tb_F, 2) * math.pow(gamma_api, 2))
        return Tc_R * 5 / 9

    @staticmethod
    def _kesler_lee(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Кеслера-Ли (Kesler-Lee, 1976)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K
        :return: Критическая температура в K
        """
        Tb_R = Tb_K * 9 / 5
        Tc_R = (341.7 + 811 * gamma + (0.4244 + 0.1174 * gamma) * Tb_R + ((0.4669 - 3.2623 * gamma) * 1e5) / Tb_R)
        return Tc_R * 5 / 9

    @staticmethod
    def _pedersen(gamma: float, M: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Педерсен (Pedersen, 1988)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)
        :return: Критическая температура в K
        """
        return 163.12 * gamma + 86.052 * math.log(M) + 0.43475 * M - (1877.4 / M)

    @staticmethod
    def _standing(gamma: float, M: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Стэндинга (Standing, 1977)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)
        :return: Критическая температура в K
        """
        if M <= 71.2:
            raise ValueError(f'Молярная масса {M} д.б. строго больше минимального значения 71.2')
        return 338 + 202 * math.log10(M - 71.2) + (1361 * math.log10(M) - 2111) * math.log10(gamma)

    @staticmethod
    def _sim_daubert(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Сима-Дауберта (Sim-Daubert, 1980)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическая температура в K
        """
        Tb_R = Tb_K * 9 / 5
        Tc_R = math.exp(3.9934718 * math.pow(Tb_R, 0.08615) * math.pow(gamma, 0.04614))
        return Tc_R * 5 / 9

    @staticmethod
    def _riazi_daubert(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Риази-Дауберта (Riazi-Daubert, 1980)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическая температура в K
        """
        Tb_R = Tb_K * 9 / 5
        Tc_R = 24.27871 * math.pow(Tb_R, 0.58848) * math.pow(gamma, 0.3596)
        return Tc_R * 5 / 9

    @staticmethod
    def _mogoulas_tassios(gamma: float, M: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Могоуласа-Тассиоса (Mogoulas, Tassios, 1990)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)

        :return: Критическая температура, K
        """

        Tc_R = -1274.4 + 0.792 * M + 1971 * gamma - 27000 / M + 707.4 / gamma
        return Tc_R * 5 / 9

    @staticmethod
    def _twu(Tb_K: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Тву (Twu, 1984)
        :param Tb_K: Температура кипения в K

        :return: Критическая температура в K
        """
        Tb_R = Tb_K * 9 / 5
        Tc_R = Tb_R / (0.533272 + 0.191017 * 1e-3 * Tb_R + 0.779681 * 1e-7 * math.pow(Tb_R, 2)
                       - 0.284376 * 1e-10 * math.pow(Tb_R, 3) + 0.959468 * 1e28 / math.pow(Tb_R, 13))
        return Tc_R * 5 / 9

    @staticmethod
    def _watansiri_owens_starling(gamma: float, Tb_K: float, M: float) -> float:
        """
        Рассчитывает критическую температуру по корреляции Ватансири-Овенса-Старлинга (Watansiri, Owens, Starling, 1985)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K
        :param M: Молярная масса в г/моль (g/mol)

        :return: Критическая температура в K
        """
        Tb_R = Tb_K * 9 / 5
        ln_Tc_R = (-0.0650504 - 0.0005217 * Tb_R + 0.03095 * math.log(M) + 1.11067 * math.log(Tb_R)
                   + M * (0.078154 * math.pow(gamma, 0.5) - 0.061061 * math.pow(gamma, 1 / 3) - 0.016943 * gamma))
        Tc_R = math.exp(ln_Tc_R)
        return Tc_R * 5 / 9

    def get_correlation(self, method: str) -> Callable:
        """
        Возвращает функцию корреляции по названию
        :param method: Название метода (e.g. Roess, Nokey, Cavett, Kesler Lee, Pedersen, Standing, Sim Daubert, Riazi Daubert, Mogoulas Tassios, Twu, Watansiri Owens Starling)
        """

        method_map = {
            'roess': self._roess,
            'nokey': self._nokey,
            'cavett': self._cavett,
            'kesler lee': self._kesler_lee,
            'pedersen': self._pedersen,
            'standing': self._standing,
            'sim daubert': self._sim_daubert,
            'riazi daubert': self._riazi_daubert,
            'mogoulas tassios': self._mogoulas_tassios,
            'twu': self._twu,
            'watansiri owens starling': self._watansiri_owens_starling,
        }
        _method = method.lower()
        if not _method in method_map:
            raise ValueError(f"CriticalTemperatureCorrelation: Unknown correlation method: {method}")
        return method_map[_method]

    @staticmethod
    def get_required_params(method: str) -> list:
        """
        Возвращает список требуемых параметров для корреляции
        """
        params_map = {
            'roess': ['gamma', 'Tb_K'],
            'nokey': ['gamma', 'Tb_K'],
            'cavett': ['gamma', 'Tb_K'],
            'kesler lee': ['gamma', 'Tb_K'],
            'pedersen': ['gamma', 'M'],
            'standing': ['gamma', 'M'],
            'sim daubert': ['gamma', 'Tb_K'],
            'riazi daubert': ['gamma', 'Tb_K'],
            'mogoulas tassios': ['gamma', 'M'],
            'twu': ['Tb_K', ],
            'watansiri owens starling': ['gamma', 'Tb_K', 'M'],
        }
        _method = method.lower()
        if _method not in params_map:
            raise ValueError(f"CriticalTemperatureCorrelation: Unknown correlation method: {method}")
        return params_map[_method]


class CriticalPressureCorrelation:
    """
    Класс, содержащий корреляции для расчета критического давления
    """

    @staticmethod
    def _kesler_lee(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Кеслера-Ли (Kesler, Lee, 1976)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическое давление, bar
        """
        Tb_R = Tb_K * 9 / 5

        first = 8.3634 - 0.0566 / gamma
        second = - (0.24244 + (2.2898 / gamma) + (0.11857 / math.pow(gamma, 2))) * 1e-3 * Tb_R
        third = (1.4685 + (3.648 / gamma) + (0.47227 / math.pow(gamma, 2))) * 1e-7 * math.pow(Tb_R, 2)
        fourth = - (0.42019 + (1.6977 / math.pow(gamma, 2))) * 1e-10 * math.pow(Tb_R, 3)
        ln_Pc_psia = sum([first, second, third, fourth])
        Pc_psia = math.exp(ln_Pc_psia)
        return Pc_psia * 0.0689476

    @staticmethod
    def _riazi_daubert(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Риази-Дауберта (Riazi, Daubert, 1980)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическое давление, bar
        """
        Tb_R = Tb_K * 9 / 5
        Pc_psia = 3.12281 * 1e9 * math.pow(Tb_R, -2.3125) * math.pow(gamma, 2.3201)
        return Pc_psia * 0.0689476

    @staticmethod
    def _cavett(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Каветта (Cavett, 1962)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическое давление, bar
        """
        Tb_F = Tb_K * 9 / 5 - 459.67
        gamma_api = 141.5 / gamma - 131.5

        log_Pc_psia = (
                2.8290406
                + (0.94120109 * 1e-3) * Tb_F
                - (0.30474749 * 1e-5) * math.pow(Tb_F, 2)
                - (0.2087611 * 1e-4) * gamma_api * Tb_F
                + (0.15184103 * 1e-8) * math.pow(Tb_F, 3)
                + (0.11047899 * 1e-7) * gamma_api * math.pow(Tb_F, 2)
                - (0.48271599 * 1e-7) * math.pow(gamma_api, 2) * Tb_F
                + (0.13949619 * 1e-9) * math.pow(gamma_api, 2) * math.pow(Tb_F, 2)
        )

        Pc_psia = math.pow(10, log_Pc_psia)
        return Pc_psia * 0.0689476

    @staticmethod
    def _pedersen(gamma: float, M: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Педерсен (Pedersen, 1988)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)

        :return: Критическое давление, bar
        """
        return math.exp(-0.13408 + 2.5019 * gamma + (208.46 / M) - (3987.2 / math.pow(M, 2)))

    @staticmethod
    def _standing(gamma: float, M: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Стэндинга (Standing, 1977)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)

        :return: Критическое давление, bar
        """
        if M <= 53.7:
            raise ValueError(f'Молярная масса {M} д.б. больше минимального значения 61.1')
        Pc_mpa = 8.191 - 2.97 * math.log10(M - 61.1) + (15.99 - 5.87 * math.log10(M - 53.7)) * (gamma - 0.8)
        return Pc_mpa * 10

    @staticmethod
    def _sim_daubert(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Сима-Дауберта (Sim, Daubert, 1980)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критическое давление, bar
        """
        Tb_R = Tb_K * 9 / 5
        Pc_psia = 3.48242 * 1e9 * math.pow(Tb_R, -2.3177) * math.pow(gamma, 2.4853)
        return Pc_psia * 0.0689476

    @staticmethod
    def _mogoulas_tassios(gamma: float, M: float) -> float:
        """
        Рассчитывает критическое давление по корреляции Могоуласа-Тассиоса (Mogoulas, Tassios, 1990)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)

        :return: Критическое давление, bar
        """
        ln_Pc_psia = 0.01901 - 0.0048442 * M + 0.13239 * gamma + (227 / M) - (1.1663 / gamma) + 1.2702 * math.log(M)
        Pc_psia = math.exp(ln_Pc_psia)
        return Pc_psia * 0.0689476

    @staticmethod
    def _twu(gamma: float, Tb_K: float):
        # TODO
        ...

    @staticmethod
    def _watansiri_owens_starling(gamma: float, Tb_K: float, M: float) -> float:
        # TODO
        ...

    @staticmethod
    def _pc_from_eos(gamma, M, Tc):
        # TODO
        ...

    def get_correlation(self, method: str) -> Callable:
        """
        Возвращает функцию корреляции по названию
        :param method: Название метода (e.g. Cavett, Kesler Lee, Pedersen, Standing, Sim Daubert, Riazi Daubert, Mogoulas Tassios)
        """
        method_map = {
            'kesler lee': self._kesler_lee,
            'riazi daubert': self._riazi_daubert,
            'cavett': self._cavett,
            'pedersen': self._pedersen,
            'standing': self._standing,
            'sim daubert': self._sim_daubert,
            'mogoulas tassios': self._mogoulas_tassios
        }

        _method = method.lower()
        if not _method in method_map:
            raise ValueError(f"CriticalPressureCorrelation: Unknown correlation method: {method}")
        return method_map[_method]

    @staticmethod
    def get_required_params(method: str) -> list:
        """
        Возвращает список требуемых параметров для корреляции
        :param method: Название метода (e.g. Cavett, Kesler Lee, Pedersen, Standing, Sim Daubert, Riazi Daubert, Mogoulas Tassios)
        """

        params_map = {
            'kesler lee': ['gamma', 'Tb_K'],
            'riazi daubert': ['gamma', 'Tb_K'],
            'cavett': ['gamma', 'Tb_K'],
            'pedersen': ['gamma', 'M'],
            'standing': ['gamma', 'M'],
            'sim daubert': ['gamma', 'Tb_K'],
            'mogoulas tassios': ['gamma', 'M']
        }

        _method = method.lower()
        if _method not in params_map:
            raise ValueError(f"CriticalPressureCorrelation: Unknown correlation method: {method}")
        return params_map[_method]


class AcentricFactorCorrelation:
    """
    Класс, содержащий корреляции для расчета ацентрического фактора
    """

    def get_correlation(self, method: str) -> Callable:
        """
        Возвращает функцию корреляции по названию
        :param method: Название метода (e.g. Edmister, Riazi Al Sahhaf, Mogoulas Tassios, Kesler Lee)
        """
        method_map = {
            'kesler lee': self._kesler_lee,
            'riazi al sahhaf': self._riazi_al_sahhaf,
            'edmister': self._edmister,
            'mogoulas tassios': self._mogoulas_tassios,
        }

        _method = method.lower()
        if not _method in method_map:
            raise ValueError(f"AcentricFactorCorrelation: Unknown correlation method: {method}")
        return method_map[_method]

    @staticmethod
    def get_required_params(method: str) -> list:
        """
        Возвращает список требуемых параметров для корреляции
        :param method: Название метода (e.g. Edmister, Riazi Al Sahhaf, Mogoulas Tassios, Kesler Lee)
        """
        params_map = {
            'edmister': ['Pc_bar', 'Tc_K', 'Tb_K'],
            'riazi al sahhaf': ['M'],
            'kesler lee': ['Pc_bar', 'Tc_K', 'Tb_K', 'Kw'],
            'mogoulas tassios': ['gamma', 'M']
        }
        _method = method.lower()
        if _method not in params_map:
            raise ValueError(f"AcentricFactorCorrelation: Unknown correlation method: {method}")
        return params_map[_method]

    @staticmethod
    def _edmister(Pc_bar: float, Tc_K: float, Tb_K: float) -> float:
        """
        Рассчитывает ацентрический фактор по корреляции Эдмистера (Edmister, 1958)
        :param Pc_bar: Критическое давление, bar
        :param Tc_K: Критическая температура, K
        :param Tb_K: Температура кипения, K

        :return: Ацентрический фактор, []
        """
        Pc_psia = Pc_bar * 14.50377
        Tc_R = Tc_K * 1.8
        Tb_R = Tb_K * 1.8

        return (3 / 7) * (math.log10(Pc_psia / 14.7) / (Tc_R / Tb_R - 1)) - 1

    @staticmethod
    def _riazi_al_sahhaf(M: float) -> float:
        """
        Рассчитывает ацентрический фактор по корреляции Риази - Аль-Саххаф (Riazi, Al-Sahhaf, 1996)
        :param M: Молярная масса в г/моль (g/mol)

        :return: Ацентрический фактор, []
        """
        return - (0.3 - math.exp(-6.252 + 3.64457 * math.pow(M, 0.1)))

    @staticmethod
    def _mogoulas_tassios(gamma: float, M: float) -> float:
        """
        Рассчитывает ацентрический фактор по корреляции Могоуласа-Тассиоса (Mogoulas, Tassios, 1990)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса в г/моль (g/mol)

        :return: Ацентрический фактор, []
        """
        return -0.64235 + 0.00014667 * M + 0.021876 * gamma - 4.559 / M + 0.21699 * math.log(M)

    @staticmethod
    def _kesler_lee(Pc_bar: float, Tc_K: float, Tb_K: float, Kw: float) -> float:
        """
        Рассчитывает ацентрический фактор по корреляции Кеслера-Ли (Kesler, Lee, 1975-1976)
        :param Pc_bar: Критическое давление, bar
        :param Tc_K: Критическая температура, K
        :param Tb_K: Температура кипения, K
        :param Kw: Фактор Ватсона

        :return: Ацентрический фактор, []
        """

        Pc_psia = Pc_bar * 14.50377
        Tc_R = Tc_K * 1.8
        Tb_R = Tb_K * 1.8

        Tbr = Tb_R / Tc_R

        if Tbr < 0.8:
            num = (
                    -math.log(Pc_psia / 14.7)
                    - 5.92714
                    + 6.09648 / Tbr
                    + 1.28862 * math.log(Tbr)
                    - 0.169347 * math.pow(Tbr, 6)
            )
            den = (
                    15.2518
                    - 15.6875 / Tbr
                    - 13.4721 * math.log(Tbr)
                    + 0.43577 * math.pow(Tbr, 6)
            )
            omega = num / den
        else:
            omega = (
                    -7.904
                    + 0.1352 * Kw
                    - 0.007465 * math.pow(Kw, 2)
                    + 8.359 * Tbr
                    + (1.408 - 0.01063 * Kw) / Tbr
            )

        return omega


class CriticalVolumeCorrelation:
    """
    Класс, содержащий корреляции для расчета критического объема
    """

    def get_correlation(self, method: str) -> Callable:
        """
        Возвращает функцию корреляции по названию
        :param method: Название метода (e.g. Hall Yarborough, Riazi Daubert, Reid, Lohrenz)
        """
        method_map = {
            'hall yarborough': self._hall_yarborough,
            'riazi daubert': self._riazi_daubert,
            'reid': self._reid,
            'lohrenz': self._lohrenz,
        }

        _method = method.lower()
        if not _method in method_map:
            raise ValueError(f"CriticalVolumeCorrelation: Unknown correlation method: {method}")
        return method_map[_method]

    @staticmethod
    def get_required_params(method: str) -> list:
        """
        Возвращает список требуемых параметров для корреляции
        :param method: Название метода (e.g. Hall Yarborough, Riazi Daubert, Reid, Lohrenz)
        """
        params_map = {
            'hall yarborough': ['gamma', 'M'],
            'riazi daubert': ['gamma', 'Tb_K'],
            'reid': ['af', 'Pc_bar', 'Tc_K'],
            'lohrenz': ['gamma', 'M']
        }
        _method = method.lower()
        if _method not in params_map:
            raise ValueError(f"CriticalVolumeCorrelation: Unknown correlation method: {method}")
        return params_map[_method]

    @staticmethod
    def _riazi_daubert(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает критический объем по корреляции Риази-Дауберта (Riazi, Daubert, 1980)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Критический объем, cm3/mol
        """
        Tb_R = Tb_K * 9 / 5
        Vc_ft3_lbmol = (7.0434 * 1e-7) * math.pow(Tb_R, 2.3829) * math.pow(gamma, -1.683)
        return Vc_ft3_lbmol * 62.42796

    @staticmethod
    def _hall_yarborough(gamma: float, M: float) -> float:
        """
        Рассчитывает критический объем по корреляции Холла-Ярборо (Hall, Yarborough, 1971)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса, г/моль (g/mol)

        :return: Критический объем, cm3/mol
        """
        Vc_ft3_lbmol = 0.025 * math.pow(M, 1.15) * math.pow(gamma, -0.7935)
        return Vc_ft3_lbmol * 62.42796

    @staticmethod
    def _reid(af: float, Pc_bar: float, Tc_K: float) -> float:
        """
        Рассчитывает критический объем по корреляции Рейд (Reid et al., 1977)
        :param af: Ацентрический фактор
        :param Pc_bar: Критическое давление, бар
        :param Tc_K: Критическая температура, K

        :return: Критический объем, cm3/mol
        """
        return (0.2918 - 0.0928 * af) * CONSTANT_R * Tc_K / Pc_bar

    @staticmethod
    def _lohrenz(gamma: float, M: float) -> float:
        """
        Рассчитывает критический объем по корреляции Лоренца (Lohrenz et al., 1964)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса, г/моль (g/mol)

        :return: Критический объем, cm3/mol
        """
        Vc_ft3_lbmol = 21.573 + 0.015122 * M - 27.656 * gamma + 0.070615 * M * gamma
        return Vc_ft3_lbmol * 62.42796

    @staticmethod
    def _riedel():
        # TODO
        ...


class KWatsonCorrelation:
    """
    Класс, содержащий корреляции для расчета фактора Ватсона
    """

    def get_correlation(self, method: str) -> Callable:
        """
        Возвращает функцию корреляции по названию
        :param method: Название метода (e.g. K Watson, Riazi Daubert)
        """
        method_map = {
            'k watson': self._k_watson,
            'riazi daubert': self._riazi_daubert,
        }

        _method = method.lower()
        if not _method in method_map:
            raise ValueError(f"KWatsonCorrelation: Unknown correlation method: {method}")
        return method_map[_method]

    @staticmethod
    def get_required_params(method: str) -> list:
        """
        Возвращает список требуемых параметров для корреляции
        :param method: Название метода (e.g. K Watson, Riazi Daubert)
        """
        params_map = {
            'k watson': ['gamma', 'Tb_K'],
            'riazi daubert': ['gamma', 'M'],
        }
        _method = method.lower()
        if _method not in params_map:
            raise ValueError(f"KWatsonCorrelation: Unknown correlation method: {method}")
        return params_map[_method]

    @staticmethod
    def _k_watson(gamma: float, Tb_K: float) -> float:
        """
        Рассчитывает фактор Ватсона (Universal Oil Products (UOP) Characterization Factor)
        :param gamma: Относительная плотность (Specific gravity)
        :param Tb_K: Температура кипения в K

        :return: Фактор Ватсона
        """
        Tb_R = Tb_K * 9 / 5
        return math.pow(Tb_R, 1 / 3) / gamma

    @staticmethod
    def _riazi_daubert(gamma: float, M: float) -> float:
        """
        Рассчитывает фактор Ватсона (Universal Oil Products (UOP) Characterization Factor)
        :param gamma: Относительная плотность (Specific gravity)
        :param M: Молярная масса, г/моль (g/mol)

        :return: Фактор Ватсона
        """
        return 4.5579 * math.pow(M, 0.15178) * math.pow(gamma, -0.84573)


class ShiftParameterCorrelation:
    """
    Класс, содержащий корреляции для расчета шифт-параметра
    """

    def get_correlation(self, method: str) -> Callable:
        """
        Возвращает функцию корреляции по названию
        :param method: Название метода (e.g. Jhaveri Youngren, SRK, PR)
        """
        method_map = {
            'jhaveri youngren': self._jhaveri_youngren,
            'srk': self._srk,
            'pr': self._pr,
            '': lambda: 0.0,
            # 'BRS': self._brs,  # TODO
        }

        _method = method.lower()
        if not _method in method_map:
            raise ValueError(f"ShiftParameterCorrelation: Unknown correlation method: {method}")
        return method_map[_method]

    @staticmethod
    def get_required_params(method: str) -> list:
        """
        Возвращает список требуемых параметров для корреляции
        :param method: Название метода (e.g. Jhaveri Youngren, SRK, PR)
        """
        params_map = {
            'jhaveri youngren': ['M', 'Kw'],
            'srk': ['af', ],
            'pr': ['af', ],
            '': [],
            # 'BRS': [],  # TODO

        }
        _method = method.lower()
        if _method not in params_map:
            raise ValueError(f"ShiftParameterCorrelation: Unknown correlation method: {method}")
        return params_map[_method]

    @staticmethod
    def _jhaveri_youngren(M: float, Kw: float) -> float:
        """
        Рассчитывает шифт-параметр s_i (s_i = c_i / b_i) по корреляции Явери-Юнгрен (Jhaveri, Youngren, 1988)
        :param M: Молярная масса, г/моль (g/mol)
        :param Kw: Фактор Ватсона

        :return: Шифт-параметр
        """

        # aromatic
        if 8.5 < Kw < 11:
            a0 = 2.516
            a1 = 0.2008

        # naften
        elif 11 < Kw < 12.5:
            a0 = 3.004
            a1 = 0.2324

        # parafin
        elif 12.5 < Kw < 13.5:
            a0 = 2.258
            a1 = 0.1823

        else:
            return 0.0

        return 1 - (a0 / (math.pow(M, a1)))

    @staticmethod
    def _srk(af: float) -> float:
        """
        Рассчитывает шифт-параметр s_i (s_i = c_i / b_i) для уравнения SRK
        :param af: Ацентрический фактор

        :return: Шифт-параметр
        """
        z_ra = 0.29056 - 0.08775 * af
        # return 0.40768 * (CONSTANT_R * Tc_K / Pc_bar) * (0.29441 - z_ra)
        return 4.70545 * (0.29441 - z_ra)

    @staticmethod
    def _pr(af: float) -> float:
        """
        Рассчитывает шифт-параметр s_i (s_i = c_i / b_i) для уравнения PR
        :param af: Ацентрический фактор

        :return: Шифт-параметр
        """
        z_ra = 0.29056 - 0.08775 * af
        # return 0.50033 * (CONSTANT_R * Tc_K / Pc_bar) * (0.25969 - z_ra)
        return 6.43098 * (0.25969 - z_ra)

    @staticmethod
    def _brs():
        # TODO
        ...


property_classes = {
    'critical_temperature': CriticalTemperatureCorrelation,
    'critical_pressure': CriticalPressureCorrelation,
    'acentric_factor': AcentricFactorCorrelation,
    'critical_volume': CriticalVolumeCorrelation,
    'Kw': KWatsonCorrelation,
    'shift_parameter': ShiftParameterCorrelation
}


class PlusComponentProperties:
    """
    Main class to calculate C7+ components properties.
    """

    def __init__(self, M: float, gamma: float, Tb: float, correlations_config: Dict[str, str], *, Tc: float = None,
                 Pc: float = None, Kw: float = None, af: float = None):

        self.correlations_config = correlations_config
        self.data = {'molar_mass': M, 'gamma': gamma, 'Tb': Tb}

        if Pc is not None:
            self.data['critical_pressure'] = Pc

        if Tc is not None:
            self.data['critical_temperature'] = Tc

        if Kw is not None:
            self.data['Kw'] = Kw

        if af is not None:
            self.data['acentric_factor'] = af

    def calculate_property(self, property_name: str) -> float:
        """
        Универсальный метод расчета любого свойства
        """

        if property_name not in property_classes:
            raise ValueError(f"PlusComponentProperties: Unknown property: {property_name}")

        method = self.correlations_config.get(property_name)
        if method is None:
            raise ValueError(f"PlusComponentProperties: No correlation specified for {property_name}")

        calculator = property_classes[property_name]

        try:
            correlation_func = calculator().get_correlation(method.lower())
            required_params = calculator().get_required_params(method.lower())
        except ValueError as e:
            raise ValueError(f"Invalid correlation for {property_name}: {e}")

        # Подготовка параметров
        params = {}
        for param in required_params:
            if param == 'gamma':
                value = self.data.get('gamma')
            elif param == 'Tb_K':
                value = self.data.get('Tb')
            elif param == 'M':
                value = self.data.get('molar_mass')
            elif param == 'Kw':
                value = self.data.get('Kw')
            elif param == 'Tc_K':
                value = self.data.get('critical_temperature')
            elif param == 'Pc_bar':
                value = self.data.get('critical_pressure')
            else:
                value = self.data.get('acentric_factor')

            if value is None:
                raise ValueError(f"Missing required parameter '{param}' for {method}")

            params[param] = value

        return correlation_func(**params)

    def calculate_all(self):

        self.data['Kw'] = self.calculate_property('Kw')

        self.data['critical_temperature'] = self.calculate_property('critical_temperature')

        self.data['critical_pressure'] = self.calculate_property('critical_pressure')

        self.data['acentric_factor'] = self.calculate_property('acentric_factor')

        self.data['critical_volume'] = self.calculate_property('critical_volume')

        self.data['shift_parameter'] = self.calculate_property('shift_parameter')
