'''Module for viscosity calculations'''

from abc import ABC
import math

class Viscosity(ABC):
    '''Abstract class to calculate viscosity'''
    def calculate(self):
        
        pass


class LBC(Viscosity):
    def __init__(self,
                 mole_fractions: dict,
                 composition_data : dict,
                 phase_density : float,
                 mw : float,
                 temperature : float,
                 alpha0 : float = 0.1023,
                 alpha1 : float = 0.023364,
                 alpha2 : float = 0.058533,
                 alpha3 : float = -0.040758,
                 alpha4 : float = 0.0093324):

        self.mole_fractions = mole_fractions
        self.composition_data = composition_data
        self.phase_density = phase_density
        self.phase_mw = mw
        self.temperature = temperature
        self.alpha0 = alpha0
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.alpha4 = alpha4

    def _calculate_epsilon_parameter(self):
        xi_tci_sum = sum([self.mole_fractions[key] * self.composition_data['critical_temperature'][key] for key in list(self.mole_fractions.keys())])
        xi_mi_sum = sum([self.mole_fractions[key] * self.composition_data['molar_mass'][key]  for key in list(self.mole_fractions.keys())])
        xi_pci_sum = sum([self.mole_fractions[key] * (self.composition_data['critical_pressure'][key] * 9.86923) for key in list(self.mole_fractions.keys())])

        return math.pow(xi_tci_sum, 1/6) / (math.pow(xi_mi_sum, 1/2) * math.pow(xi_pci_sum, 2/3))


    def _calculate_mu0_mod(self):
        n_i_dict = {}
        epsilon_i = {}
        for component in list(self.mole_fractions.keys()):
            epsilon_i[component] = (math.pow(self.composition_data['critical_temperature'][component], 1/6) /
                                    (math.pow(self.composition_data['molar_mass'][component] , 1/2) *
                                     math.pow(self.composition_data['critical_pressure'][component] * 9.86923, 2/3)))

            if self.temperature / self.composition_data['critical_temperature'][component] < 1.5:
                n_i_dict[component] = 34 * math.pow(10, -5)  * (1/epsilon_i[component]) * math.pow(self.temperature/ self.composition_data['critical_temperature'][component], 0.94)
            else:
                n_i_dict[component] = 17.78 * math.pow(10, -5) * (1/epsilon_i[component]) * math.pow(4.58 * self.temperature / self.composition_data['critical_temperature'][component] - 1.67, 5/8)

        sum_zi_ni_mi = sum([self.mole_fractions[key] * n_i_dict[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])
        sum_zi_mi = sum([self.mole_fractions[key] * math.pow(self.composition_data['molar_mass'][component], 1/2) for key in list(self.mole_fractions.keys())])

        return sum_zi_ni_mi / sum_zi_mi


    def _calculate_rho_reduced(self):
        v_crit_mixed = sum([self.mole_fractions[key] * self.composition_data['critical_volume'][key] for key in list(self.mole_fractions.keys())]) 
        rho_crit = 1 / v_crit_mixed
        phase_density = (self.phase_density * 62.428) / self.phase_mw

        return phase_density / rho_crit


    def calculate(self):
        epsilon = self._calculate_epsilon_parameter()
        mu_parameter = self._calculate_mu0_mod()
        rho_reduced = self._calculate_rho_reduced()
        right_part_eq = (self.alpha0 + self.alpha1 * rho_reduced + self.alpha2 * math.pow(rho_reduced, 2) +
                         self.alpha3 * math.pow(rho_reduced, 3) + self.alpha4 * math.pow(rho_reduced, 4))

        return ((math.pow(right_part_eq, 4) + math.pow(10, -4))/epsilon) + mu_parameter