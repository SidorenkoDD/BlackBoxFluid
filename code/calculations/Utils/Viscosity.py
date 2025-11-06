'''Module for viscosity calculations'''

from abc import ABC


class Viscosity(ABC):
    '''Abstract class to calculate viscosity'''
    def calculate(self):
        
        pass


class LBC(Viscosity):
    '''Class with LBC-method'''
    def __init__(self, mole_fractions: dict, composition_data, param_set: dict = {'alpha0' : 0.1023,
                                          'alpha1' : 0.023364,
                                          'alpha2' : 0.058533,
                                          'alpha3' : -0.040758,
                                          'alpha4' : 0.0093324}):
        self.param_set = param_set
        self.mole_fractions = mole_fractions
        self.composition_data = composition_data

    def _calculate_epsilon_parameter(self):
        ...

    def _calculate_mu0_i_parameter(self):
        ...

    def _calculate_mu0_parameter(self):
        ...

    def calculate(self):
        ...