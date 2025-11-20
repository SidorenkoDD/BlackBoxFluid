'''Module for viscosity calculations'''

from abc import ABC
import math

class Viscosity(ABC):
    '''Abstract class to calculate viscosity'''
    def calculate(self):
        
        pass


class LBC_from_paper(Viscosity):
    '''Class with LBC-method'''
    def __init__(self,
                 mole_fractions: dict,
                 composition_data : dict,
                 phase_volume : float,
                 temperature : float,
                 fl : float,
                 alpha0 : float = 0.1023,
                 alpha1 : float = 0.023364,
                 alpha2 : float = 0.058533,
                 alpha3 : float = -0.040758,
                 alpha4 : float = 0.0093324):

        self.mole_fractions = mole_fractions
        self.composition_data = composition_data
        self.phase_volume = phase_volume
        self.temperature = temperature
        self.fl = fl
        self.alpha0 = alpha0
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.alpha4 = alpha4

    def calculate_rho_reduced(self):
        ##TODO: в чем здесь приходит критический объем ? Он рассчитывается по корреляции и скорее всего приходит в
        # буржуйских ед. изм. 
        ## * 16018.463 ### 62.42796 
        v_crit = sum([self.mole_fractions[key] * self.composition_data['critical_volume'][key] / 16018.463 for key in list(self.mole_fractions.keys())])
        #pho_crit = self.fl / v_crit
        print(f'Vcrit {v_crit}')
        print(f'Vcrit * FL {v_crit * self.fl}')
        return self.phase_volume /(v_crit * self.fl)

    def _calculate_epsilon_parameter(self):
        xi_tci_sum = sum([self.mole_fractions[key] * self.composition_data['critical_temperature'][key] for key in list(self.mole_fractions.keys())])
        xi_mi_sum = sum([self.mole_fractions[key] * self.composition_data['molar_mass'][key] for key in list(self.mole_fractions.keys())])
        xi_pci_sum = sum([self.mole_fractions[key] * (self.composition_data['critical_pressure'][key] * 9.86923) for key in list(self.mole_fractions.keys())])

        return math.pow(xi_tci_sum, 1/6) / (math.pow(xi_mi_sum, 1/2) * math.pow(xi_pci_sum, 2/3))

    def _calculate_mu0_parameter(self):
        mu0_i_dict = {}
        for component in list(self.mole_fractions.keys()):
            if self.temperature / self.composition_data['critical_temperature'][component] < 1.5:
                mu0_i_dict[component] = (math.pow(self.composition_data['molar_mass'][component], 0.5) * math.pow((self.composition_data['critical_pressure'][component] * 9.86923), 2/3) / (math.pow(10, 5) * math.pow(self.composition_data['critical_temperature'][component] * 1.8, 1/6))) * 34 * math.pow(self.temperature / self.composition_data['critical_temperature'][component], 0.94)
            else:
                mu0_i_dict[component] = (math.pow(self.composition_data['molar_mass'][component], 0.5) * math.pow((self.composition_data['critical_pressure'][component] * 9.86923), 2/3) / (math.pow(10, 5) * math.pow(self.composition_data['critical_temperature'][component] * 1.8, 1/6))) * 17.78 * math.pow(4.58 * self.temperature / self.composition_data['critical_temperature'][component] - 1.67, 0.625)

        xi_mui_mi = sum([ self.mole_fractions[key] * mu0_i_dict[key] * math.sqrt(self.composition_data['molar_mass'][key]) for key in list(self.mole_fractions.keys())])
        xi_mi = sum([ self.mole_fractions[key] * math.sqrt(self.composition_data['molar_mass'][key]) for key in list(self.mole_fractions.keys())])

        return xi_mui_mi / xi_mi

    def _calculate_mu0_mod(self):
        n_i_dict = {}
        epsilon_i = {}
        for component in list(self.mole_fractions.keys()):
            ##TODO: PRESSURE
            epsilon_i[component] = (math.pow(self.composition_data['critical_temperature'][component], 1/6) /
                                    (math.pow(self.composition_data['molar_mass'][component], 1/2) *
                                     math.pow(self.composition_data['critical_pressure'][component] * 9.86923, 2/3)))

            if self.temperature / self.composition_data['critical_temperature'][component] < 1.5:
                n_i_dict[component] = 34 * math.pow(10, -5)  * (1/epsilon_i[component]) * math.pow(self.temperature / self.composition_data['critical_temperature'][component], 0.94)
            else:
                n_i_dict[component] = 17.78 * math.pow(10, -5) * (1/epsilon_i[component]) * math.pow(4.58 * self.temperature / self.composition_data['critical_temperature'][component] - 1.67, 5/8)

        sum_zi_ni_mi = sum([self.mole_fractions[key] * n_i_dict[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])
        sum_zi_mi = sum([self.mole_fractions[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])

        return sum_zi_ni_mi / sum_zi_mi

    def calculate(self):
        epsilon = self._calculate_epsilon_parameter()
        rho_reduced = self.calculate_rho_reduced()
        right_part_equation = self.alpha0 + self.alpha1 * rho_reduced + self.alpha2 * math.pow(rho_reduced, 2) + self.alpha3 * math.pow(rho_reduced, 3) + self.alpha4 * math.pow(rho_reduced, 4)
        mu0 = self._calculate_mu0_parameter()
        mu0_mod = self._calculate_mu0_mod()
        print(f'MU_0: {mu0}')
        print(f'MU0_mod : {mu0_mod}')

        print(f'solve mu_base {((math.pow(right_part_equation, 4) - math.pow(10, -4)) / epsilon) + mu0}')
        print(f'solve mu_mod {((math.pow(right_part_equation, 4) - math.pow(10, -4)) / epsilon) + mu0_mod}')
        return ((math.pow(right_part_equation, 4) - math.pow(10, -4)) / epsilon) + mu0_mod


class LBCfromPVTSIM(Viscosity):
        def __init__(self,
                 mole_fractions: dict,
                 composition_data : dict,
                 phase_density : float,
                 temperature : float,
                 alpha0 : float = 0.1023,
                 alpha1 : float = 0.023364,
                 alpha2 : float = 0.058533,
                 alpha3 : float = -0.040758,
                 alpha4 : float = 0.0093324):

            self.mole_fractions = mole_fractions
            self.composition_data = composition_data
            self.phase_density = phase_density
            self.temperature = temperature
            self.alpha0 = alpha0
            self.alpha1 = alpha1
            self.alpha2 = alpha2
            self.alpha3 = alpha3
            self.alpha4 = alpha4


        def _calc_epsilon(self):
            xi_tci_sum = sum([self.mole_fractions[key] * self.composition_data['critical_temperature'][key] for key in list(self.mole_fractions.keys())])
            xi_mi_sum = sum([self.mole_fractions[key] * self.composition_data['molar_mass'][key] for key in list(self.mole_fractions.keys())])
            ##TODO: PRESSURE
            xi_pci_sum = sum([self.mole_fractions[key] * self.composition_data['critical_pressure'][key] * 10 for key in list(self.mole_fractions.keys())]) 

            return math.pow(xi_tci_sum, 1/6) * math.pow(xi_mi_sum, -1/2) * math.pow(xi_pci_sum, -2/3)


        def _calc_n_parameter(self):
            n_i_dict = {}
            epsilon_i = {}
            for component in list(self.mole_fractions.keys()):
                ##TODO: PRESSURE
                epsilon_i[component] = math.pow(self.composition_data['critical_temperature'][component], 1/6) / (math.pow(self.composition_data['molar_mass'][component], -1/2) * math.pow(self.composition_data['critical_pressure'][component] * 10, -2/3))
                if self.temperature / self.composition_data['critical_temperature'][component] <= 1.5:
                    n_i_dict[component] = 34 * math.pow(10, -5) * (1/epsilon_i[component]) * math.pow(self.temperature / self.composition_data['critical_temperature'][component], 0.94)
                else:
                    n_i_dict[component] = 17.78 * math.pow(10, -5) * (1/epsilon_i[component]) * math.pow(4.58 * self.temperature / self.composition_data['critical_temperature'][component] - 1.67, 5/8)

            sum_zi_ni_mi = sum([self.mole_fractions[key] * n_i_dict[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])
            sum_zi_mi = sum([self.mole_fractions[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])

            return sum_zi_ni_mi / sum_zi_mi

        def calculate_rho_reduced(self):
            ##TODO: CRIT VOLUME
            v_crit = sum([self.mole_fractions[key] * 16018.463 / self.composition_data['critical_volume'][key] for key in list(self.mole_fractions.keys())])
            pho_crit = 1 / v_crit

            return self.phase_density / pho_crit

        def calculate(self):
            epsilon = self._calc_epsilon()
            rho_reduced = self.calculate_rho_reduced()
            right_part_equation = self.alpha0 + self.alpha1 * rho_reduced + self.alpha2 * math.pow(rho_reduced, 2) + self.alpha3 * math.pow(rho_reduced, 3) + self.alpha4 * math.pow(rho_reduced, 4)
            mu0 = self._calc_n_parameter()
            print(mu0)
            return ((math.pow(right_part_equation, 4) - math.pow(10, -4)) / epsilon) + mu0


class LBCfromWhitsonwiki(Viscosity):
    def __init__(self,
                 mole_fractions: dict,
                 composition_data : dict,
                 phase_density : float,
                 temperature : float,
                 alpha0 : float = 0.1023,
                 alpha1 : float = 0.023364,
                 alpha2 : float = 0.058533,
                 alpha3 : float = -0.04758,
                 alpha4 : float = 0.0093324):

        self.mole_fractions = mole_fractions
        self.composition_data = composition_data
        self.phase_density = phase_density
        self.temperature = temperature
        self.alpha0 = alpha0
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.alpha4 = alpha4

    def _calculate_epsilon_parameter(self):
        xi_tci_sum = sum([self.mole_fractions[key] * self.composition_data['critical_temperature'][key] for key in list(self.mole_fractions.keys())])
        xi_mi_sum = sum([self.mole_fractions[key] * self.composition_data['molar_mass'][key] for key in list(self.mole_fractions.keys())])
        xi_pci_sum = sum([self.mole_fractions[key] * self.composition_data['critical_pressure'][key] * 10 for key in list(self.mole_fractions.keys())])

        return math.pow(xi_tci_sum, 1/6) / (math.pow(xi_mi_sum, 1/2) * math.pow(xi_pci_sum, 2/3))

    def _calculate_mu(self):
        n_i_dict = {}
        epsilon_i = {}
        for component in list(self.mole_fractions.keys()):
            ##TODO: PRESSURE
            epsilon_i[component] = (math.pow(self.composition_data['critical_temperature'][component], 1/6) /
                                    (math.pow(self.composition_data['molar_mass'][component], 1/3) *
                                     math.pow(self.composition_data['critical_pressure'][component] * 10, 2/3)))

            if self.temperature / self.composition_data['critical_temperature'][component] < 1.5:
                n_i_dict[component] = 34 * math.pow(10, -5) * (1/epsilon_i[component]) * math.pow(self.temperature / self.composition_data['critical_temperature'][component], 0.94)
            else:
                n_i_dict[component] = 17.78 * math.pow(10, -5) * (1/epsilon_i[component]) * math.pow(4.58 * self.temperature / self.composition_data['critical_temperature'][component] - 1.67, 5/8)

        sum_zi_ni_mi = sum([self.mole_fractions[key] * n_i_dict[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])
        sum_zi_mi = sum([self.mole_fractions[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])

        return sum_zi_ni_mi / sum_zi_mi


    def _calculate_rho_reduced(self):
        v_crit = sum([self.mole_fractions[key] * self.composition_data['critical_volume'][key] for key in list(self.mole_fractions.keys())])
        pho_crit = 1 / v_crit

        return self.phase_density / pho_crit
    
    def calculate(self):
        rho_reduced = self._calculate_rho_reduced()
        right_part_eq = (self.alpha0 + self.alpha1 * rho_reduced +
                         self.alpha2 * math.pow(rho_reduced,2) + self.alpha3 * math.pow(rho_reduced,3) + 
                         self.alpha4 * math.pow(rho_reduced,4))
        mu = self._calculate_mu()
        epsilon = self._calculate_epsilon_parameter()

        return ((math.pow(right_part_eq, 4) - math.pow(10, -4)) / epsilon) + mu
