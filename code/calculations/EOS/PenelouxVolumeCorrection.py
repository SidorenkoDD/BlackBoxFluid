'''class to calculate EOS with correction'''
from calculations.EOS.EOSFactory import EOSFactory
class PenelouxVolumeCorrection:
    def __init__(self, composition,
                 composition_data,
                 p,
                 t,
                 eos : str = 'PREOS'):

        self.eos_factory = EOSFactory.create_eos(eos)
        self.composition = composition
        self.composition_data = composition_data
        self.p = p
        self.t = t

    def calculate(self):
        eos = self.eos_factory(zi = self.composition, components_properties= self.composition_data, p = self.p, t = self.t)
        eos.calc_eos_with_peneloux_correction()
        return eos.z
