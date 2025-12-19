'''class to calculate EOS with correction'''
from calculations.EOS.EOSFactory import EOSFactory
from calculations.Utils.Constants import CONSTANT_R
class PenelouxVolumeCorrection:
    def __init__(self, composition,
                 composition_data,
                 p,
                 t,
                 eos : str = 'PREOS'):

        self._eos_factory = EOSFactory.create_eos(eos)
        self._composition = composition
        self._composition_data = composition_data
        self._p = p
        self._t = t

    def calculate_eos_with_peneloux(self):
        ''''''
        eos = self._eos_factory(zi = self._composition, components_properties= self._composition_data, p = self._p, t = self._t)
        eos.calc_eos_with_peneloux_correction()
        return eos.z
    
    def update_z(self,
                 volume : float,
                 F : float):
        ''''''
        return (self._p * volume) / (F * CONSTANT_R * self._t)


    def upd_z_new(self,
                  z : float,
                  c : float):
        return z - (self._p * c) / (CONSTANT_R * self._t)