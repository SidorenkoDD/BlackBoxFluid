from copy import deepcopy

from ..Composition.PlusComponentCorrelationsV2 import PlusComponentProperties
from ..Utils.JsonDBReader import JsonDBReader
from ..Utils import BRS_EOS_DB_V2 as BRSDB
from ..Utils.Errors import NoComponentError, InvalidMolarFractionError
from ..EOS.BaseEOS import EOSType
import logging
logger = logging.getLogger('MBALPVT.PVTDataModel.PVTCore.Composition')
db = JsonDBReader().load_database('DB_V2.json')


def check_and_sort_composition(composition_dict: dict):
    # db = JsonDBReader().load_database('DB_V2.json')
    available_components = db['available_components']
    sequence_numbers = db['sequence_number']
    carbon_flags = db['carbon_flag']

    normalized_composition = {}
    c_composition = {}
    nc_composition = {}
    for component in composition_dict:

        if component not in available_components:
            raise NoComponentError(f'Компонент {component} отсутсвует в БД')

        molar_fraction = composition_dict[component]

        seqnum = sequence_numbers[component]
        carbonflag = bool(carbon_flags[component])

        if carbonflag:
            c_composition[(component, seqnum)] = molar_fraction
        else:
            nc_composition[(component, seqnum)] = molar_fraction

    c_composition = dict(sorted(c_composition.items(), key=lambda item: item[0][1]))
    nc_composition = dict(sorted(nc_composition.items(), key=lambda item: item[0][1]))

    for key in nc_composition:
        normalized_composition[key[0]] = nc_composition[key]
    for key in c_composition:
        normalized_composition[key[0]] = c_composition[key]

    return normalized_composition

def _normalize_composition(composition_dict: dict):
    normalized_composition = {}

    mol_sum = sum(list(composition_dict.values()))
    for component in composition_dict:
        molar_fraction = composition_dict[component]

        if molar_fraction <= 0.0:
            raise InvalidMolarFractionError(
                f'Мольная доля компонента {component} д.б. больше 0. Передано: {molar_fraction}')

        normalized_composition[component] = molar_fraction / mol_sum
    return normalized_composition


class Composition:
    def __init__(self, zi: dict, / , T_res: float = 373.15, eos_name: EOSType = EOSType.PREOS):

        self._composition = check_and_sort_composition(zi)
        self._T_res = T_res  # Пластовая температура
        self._eos_name = eos_name  # Уравнение состояния

        self._composition_data = {
            'molar_mass': {},
            'gamma': {},
            'Tb': {},
            'critical_pressure': {},
            'critical_temperature': {},
            'acentric_factor': {},
            'critical_volume': {},
            'shift_parameter': {},
            'peneloux_correction': {},
            'bip': {},
            'dbipdT': {},
            'c5_plus_flag': {},
            'c7_plus_flag': {},
            'carbon_flag': {},
            'Kw': {},
            'Zc': {},
            'OmegaC': {},
            'Psi': {},
            'alpha': {},
            'beta': {},
            'sigma': {},
            'delta': {},
            'a': {},
            'b': {},
            'c': {},
            'd': {},
        }

        self._fill_M_Tb_gamma_from_db()

    def _evaluate_bips(self, only_brs=False):
        if not only_brs:
            if self._eos_name == EOSType.PREOS:
                bip_func = self._calc_bip_pr
            elif self._eos_name == EOSType.SRKEOS:
                bip_func = self._calc_bip_srk
            else: # self._eos_name == 'BRSEOS'
                bip_func = self._calc_bip_brs

            for comp1 in list(self._composition):
                for comp2 in list(self._composition):
                    # self._composition_data['bip'][comp1][comp2] = bip_func(comp1, comp2, db)
                    bip, dbipdT = bip_func(comp1, comp2)
                    self._composition_data['bip'].setdefault(comp1, {})[comp2] = bip
                    self._composition_data['dbipdT'].setdefault(comp1, {})[comp2] = dbipdT

        elif self._eos_name == EOSType.BRSEOS:
            bip_func = self._calc_bip_brs
            for comp1 in list(self._composition):
                for comp2 in list(self._composition):
                    # self._composition_data['bip'][comp1][comp2] = bip_func(comp1, comp2, db)
                    bip, dbipdT = bip_func(comp1, comp2)
                    self._composition_data['bip'].setdefault(comp1, {})[comp2] = bip
                    self._composition_data['dbipdT'].setdefault(comp1, {})[comp2] = dbipdT

        else:
            pass

    def _calc_bip_pr(self, component1: str, component2: str):
        c7_plus_flag1 = self._composition_data['c7_plus_flag'][component1]
        c7_plus_flag2 = self._composition_data['c7_plus_flag'][component2]

        if any([c7_plus_flag1, c7_plus_flag2]):
            # TODO
            bip = 0.0
        else:
            bip = db['bip_pr'][component1][component2]
        return bip, 0.0

    def _calc_bip_srk(self, component1: str, component2: str):
        c7_plus_flag1 = self._composition_data['c7_plus_flag'][component1]
        c7_plus_flag2 = self._composition_data['c7_plus_flag'][component2]

        if any([c7_plus_flag1, c7_plus_flag2]):
            bip = 0.0
        else:
            bip = db['bip_srk'][component1][component2]
        return bip, 0.0

    def _calc_bip_brs(self, component1: str, component2: str):
        c5_plus_flag1 = self._composition_data['c5_plus_flag'][component1]
        c5_plus_flag2 = self._composition_data['c5_plus_flag'][component2]

        if any([c5_plus_flag1, c5_plus_flag2]):
            # comp1 - Из фракции C5+
            (comp1, _), (comp2, _) = list(sorted([(component1, c5_plus_flag1), (component2, c5_plus_flag2)],
                                                 key=lambda x: x[1], reverse=True))

            omega = self._composition_data['acentric_factor'][comp1]
            Kw = self._composition_data['Kw'][comp1]
            # logger.debug(f'{comp1} {omega} {Kw}')

            return BRSDB.evaluate_BRS_EOS_bip_for_c5_plus(comp1, comp2, self._T_res, omega, Kw)
        else:
            return BRSDB.evaluate_BRS_EOS_bip_below_c5_plus(component1, component2, self._T_res)

    def _fill_M_Tb_gamma_from_db(self):
        for component in self._composition:
            self._composition_data['molar_mass'][component] = db['molar_mass'][component]
            self._composition_data['gamma'][component] = db['gamma'][component]
            self._composition_data['Tb'][component] = db['Tb'][component]
            self._composition_data['c7_plus_flag'][component] = bool(db['c7_plus_flag'][component])
            self._composition_data['c5_plus_flag'][component] = bool(db['c5_plus_flag'][component])
            self._composition_data['carbon_flag'][component] = bool(db['carbon_flag'][component])

    def evaluate_composition_data(self, c7_plus_correlations: dict):

        # Расчет свойств отдельных компонент
        for component in self._composition:
            c7_plus_flag = self._composition_data['c7_plus_flag'][component]
            c5_plus_flag = self._composition_data['c5_plus_flag'][component]
            M = self._composition_data['molar_mass'][component]
            gamma = self._composition_data['gamma'][component]
            Tb = self._composition_data['Tb'][component]

            if c7_plus_flag:
                prop_calculator = PlusComponentProperties(gamma=gamma, Tb=Tb, M=M,
                                                          correlations_config=c7_plus_correlations)
                prop_calculator.calculate_all()

                Kw = prop_calculator.data['Kw']
                Tc = prop_calculator.data['critical_temperature']
                Pc = prop_calculator.data['critical_pressure']
                af = prop_calculator.data['acentric_factor']
                Vc = prop_calculator.data['critical_volume']
                Sshift = prop_calculator.data['shift_parameter']

            else:
                if c5_plus_flag:
                    Kw = db['Kw'][component]
                else:
                    Kw = None
                Pc = db['critical_pressure'][component]
                Tc = db['critical_temperature'][component]
                af = db['acentric_factor'][component]
                Vc = db['critical_volume'][component]

                if self._eos_name == EOSType.PREOS:
                    Sshift = db['shift_parameter_pr'][component]
                elif self._eos_name == EOSType.SRKEOS:
                    Sshift = db['shift_parameter_srk'][component]
                else:
                    Sshift = 0.0

            self._composition_data['Kw'][component] = Kw
            self._composition_data['critical_pressure'][component] = Pc
            self._composition_data['critical_temperature'][component] = Tc
            self._composition_data['acentric_factor'][component] = af
            self._composition_data['critical_volume'][component] = Vc
            self._composition_data['shift_parameter'][component] = Sshift

            # Расчет свойств, зависящих от УРС и температуры
            self._evaluate_eos_dependent_props_for_component(component)

        # Расчет коэффициентов парного взаимодействия
        #  TODO: Если значения нет в БД - расчет по Tb (см. Брусиловский)) (Расширить БД bip_pr до C10)
        self._evaluate_bips()

    def _evaluate_eos_dependent_props_for_component(self, component):

        af = self._composition_data['acentric_factor'].get(component)
        c5_plus_flag = self._composition_data['c5_plus_flag'].get(component)
        Pc = self._composition_data['critical_pressure'].get(component)
        Tc = self._composition_data['critical_temperature'].get(component)
        sshift = self._composition_data['shift_parameter'].get(component, 0.0)

        if af is None:
            logger.error(f'Отсутствует рассчитанное значение ацентрического фактора для компонента: {component}')
        elif Pc is None:
            logger.error(f'Отсутствует рассчитанное значение критического давления для компонента: {component}')
        elif Tc is None:
            logger.error(f'Отсутствует рассчитанное значение критической температуры для компонента: {component}')
        else:
            OmegaC, Zc, Psi = BRSDB.evaluate_BRS_EOS_component_params(component, af, self._eos_name, c5_plus_flag)
            self._composition_data['OmegaC'][component] = OmegaC
            self._composition_data['Zc'][component] = Zc
            self._composition_data['Psi'][component] = Psi

            alpha, beta, sigma, delta = BRSDB.calc_alpha_beta_gamma_delta(OmegaC, Zc)
            self._composition_data['alpha'][component] = alpha
            self._composition_data['beta'][component] = beta
            self._composition_data['sigma'][component] = sigma
            self._composition_data['delta'][component] = delta

            a, b, c, d = BRSDB.calc_a_b_c_d(self._T_res, Pc, Tc, alpha, beta, sigma, delta, Psi)
            self._composition_data['a'][component] = a
            self._composition_data['b'][component] = b
            self._composition_data['c'][component] = c
            self._composition_data['d'][component] = d

            self._composition_data['peneloux_correction'][component] = b * sshift

    def _evaluate_eos_dependent_props(self):
        for component in self._composition:
            self._evaluate_eos_dependent_props_for_component(component)

    def recalculate_property(self):
        # TODO: Для перерасчета отдельного свойства по корреляции
        pass

    def new_composition(self, molar_fractions: dict, deep_copy=False):
        """
        Возвращает копию состава с переданными мольными долями (компонентный состав должен совпадать!)
        """
        new_fractions = check_and_sort_composition(molar_fractions)
        if not ((len(new_fractions) == len(self._composition))
                and (set(list(new_fractions.keys())) == set(self._composition.keys()))):
            raise RuntimeError('Переданный компонентный состав не идентичен исходному')
        new_fractions = _normalize_composition(new_fractions)
        new_composition = Composition(new_fractions, T_res=self._T_res, eos_name=self._eos_name)
        new_composition._composition_data = self._composition_data if deep_copy is False else deepcopy(self._composition_data)
        return new_composition

    def normalize_composition(self):
        self._composition = _normalize_composition(self._composition)

    def edit_component_properties(self, component: str, property_name: str, value: float):
        """
        Метод позволяет изменять значение свойства для компонента

        :param component: Название компонента
        :param property_name: Название свойства ('molar_mass', 'gamma', 'Tb', 'critical_pressure',
        'critical_temperature', 'acentric_factor', 'shift_parameter', 'critical_volume')
        :param value: Значение свойства
        """

        avalible_properties = ['molar_mass', 'gamma', 'Tb', 'critical_pressure', 'critical_temperature',
                               'acentric_factor', 'shift_parameter', 'critical_volume', 'Kw', 'peneloux_correction']

        if property_name not in avalible_properties:
            raise KeyError(f'Свойство {property_name} недоступно для изменения или отсутствует!')

        if property_name == 'peneloux_correction':
            self.edit_cpen_for_component(component, value)
        else:
            self._composition_data[property_name][component] = value

        if property_name in ['critical_pressure', 'critical_temperature', 'acentric_factor']:
            self._evaluate_eos_dependent_props_for_component(component)

    def edit_bip_for_components(self, component1: str, component2: str, bip: float):
        if component1 not in self._composition:
            raise KeyError(f'Компонент {component1} отсутствует в составе!')
        if component2 not in self._composition:
            raise KeyError(f'Компонент {component2} отсутствует в составе!')
        self._composition_data['bip'][component1][component2] = bip
        self._composition_data['bip'][component2][component1] = bip

    def edit_dbipdt_for_components(self, component1: str, component2: str, dbipdt: float):
        if component1 not in self._composition:
            raise KeyError(f'Компонент {component1} отсутствует в составе!')
        if component2 not in self._composition:
            raise KeyError(f'Компонент {component2} отсутствует в составе!')
        self._composition_data['dbipdT'][component1][component2] = dbipdt
        self._composition_data['dbipdT'][component2][component1] = dbipdt

    def edit_cpen_for_component(self, component: str, cpen: float):
        b = self._composition_data['b'].get(component)
        if cpen is not None:
            self._composition_data['shift_parameter'][component] = cpen / b
            self._composition_data['peneloux_correction'][component] = cpen
        else:
            self._composition_data['shift_parameter'][component] = 0.0
            self._composition_data['peneloux_correction'][component] = 0.0

    @property
    def composition(self):
        return self._composition
        # return deepcopy(self._composition)

    @property
    def composition_data(self):
        return self._composition_data
        # return deepcopy(self._composition_data)

    @property
    def T(self):
        return self._T_res

    @T.setter
    def T(self, T: float):
        self._T_res = float(T)
        self._evaluate_eos_dependent_props()
        self._evaluate_bips(only_brs=True)

    @property
    def eos_name(self):
        return self._eos_name

    @eos_name.setter
    def eos_name(self, eos_name: EOSType):
        self._eos_name = eos_name
        self._evaluate_eos_dependent_props()
        self._evaluate_bips()
