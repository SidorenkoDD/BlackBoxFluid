'''Module for viscosity calculations'''

from abc import ABC
import math

class Viscosity(ABC):
    '''Abstract class to calculate viscosity'''
    def calculate(self):
        
        pass

class ViscosityFactory:

    @staticmethod
    def create_viscosity_object(viscosity_method):
        eos_mapping = {
            "LBC": LBC,
            "PEDERSEN": LBC,
        }
        if viscosity_method not in eos_mapping:
            raise ValueError(f"Unknown viscosity method: {viscosity_method}")
        return eos_mapping[viscosity_method]

class ViscosityFacade:
    def __init__(self):
        pass



class LBC(Viscosity):
    '''
    Class to calculate viscosity with LBC method

    Attributes
    ---------
    * mole_fractions : dict with composition mole fractions
    * composition_data : dict with all properties for all components in mole_fractions
    * phase_density : float, density for phase to calculate viscosity (from flash results)
    * mw : float, molecular weight for phase to calculate viscosity (from flash results)
    * temperature : float, temperature in K

    Methods
    ------
    * calculate_epsilon_parameter : inner method to calculate epsilon
    * calculate_mu0_mod : inner method to calculate mu0
    * calculate_rho_reduced : inner method to calculate reduced density
    * calculate : main method to calculate viscosity
    '''
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

        self._mole_fractions = mole_fractions
        self._composition_data = composition_data
        self._phase_density = phase_density
        self._phase_mw = mw
        self._temperature = temperature
        self._alpha0 = alpha0
        self._alpha1 = alpha1
        self._alpha2 = alpha2
        self._alpha3 = alpha3
        self._alpha4 = alpha4


    def _calculate_epsilon_parameter(self):
        '''
        pressure in atma
        '''
        xi_tci_sum = (sum([self._mole_fractions[key] *
                           self._composition_data['critical_temperature'][key] for key in list(self._mole_fractions.keys())]))
        xi_mi_sum = (sum([self._mole_fractions[key] *
                          self._composition_data['molar_mass'][key]  for key in list(self._mole_fractions.keys())]))
        xi_pci_sum = (sum([self._mole_fractions[key] *
                           (self._composition_data['critical_pressure'][key] * 9.86923) for key in list(self._mole_fractions.keys())]))

        return math.pow(xi_tci_sum, 1/6) / (math.pow(xi_mi_sum, 1/2) * math.pow(xi_pci_sum, 2/3))


    def _calculate_mu0_mod(self):
        '''
        pressure in atma
        '''
        n_i_dict = {}
        epsilon_i = {}
        for component in list(self._mole_fractions.keys()):
            epsilon_i[component] = (math.pow(self._composition_data['critical_temperature'][component], 1/6) /
                                    (math.pow(self._composition_data['molar_mass'][component] , 1/2) *
                                     math.pow(self._composition_data['critical_pressure'][component] * 9.86923, 2/3)))

            if self._temperature / self._composition_data['critical_temperature'][component] < 1.5:
                n_i_dict[component] = (34 * math.pow(10, -5)  * (1/epsilon_i[component]) *
                                       math.pow(self._temperature/ self._composition_data['critical_temperature'][component], 0.94))
            else:
                n_i_dict[component] = (17.78 * math.pow(10, -5) * (1/epsilon_i[component]) *
                                       math.pow(4.58 * self._temperature / self._composition_data['critical_temperature'][component] - 1.67, 5/8))

        sum_zi_ni_mi = (sum([self._mole_fractions[key] * n_i_dict[key] *
                             math.pow(self._composition_data['molar_mass'][component], 1/2) for key in list(self._mole_fractions.keys())]))
        sum_zi_mi = (sum([self._mole_fractions[key] *
                          math.pow(self._composition_data['molar_mass'][component], 1/2) for key in list(self._mole_fractions.keys())]))

        return sum_zi_ni_mi / sum_zi_mi


    def _calculate_rho_reduced(self):
        '''
        Method calculates reduced density rho / rho_crit
        v_crit is a linear mixed v_crit by molar fractions, units are ft3/lb-mol
        phase density in input in g/cm3, transforms in lb mole/ ft3
        '''
        v_crit_mixed = (sum([self._mole_fractions[key] *
                             self._composition_data['critical_volume'][key] for key in list(self._mole_fractions.keys())]))
        rho_crit = 1 / v_crit_mixed
        phase_density = (self._phase_density * 62.428) / self._phase_mw

        return phase_density / rho_crit


    def calculate(self):
        '''
        Main method to calculate viscosity

        Return
        ------
        Viscosity of the phase in cP
        '''
        epsilon = self._calculate_epsilon_parameter()
        mu_parameter = self._calculate_mu0_mod()
        rho_reduced = self._calculate_rho_reduced()
        right_part_eq = (self._alpha0 + self._alpha1 * rho_reduced + self._alpha2 * math.pow(rho_reduced, 2) +
                         self._alpha3 * math.pow(rho_reduced, 3) + self._alpha4 * math.pow(rho_reduced, 4))

        return ((math.pow(right_part_eq, 4) + math.pow(10, -4))/epsilon) + mu_parameter