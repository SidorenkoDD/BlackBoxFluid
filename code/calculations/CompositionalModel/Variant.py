from calculations.Composition.Composition import Composition
#from calculations.EOS import BaseEOS


class Variant:
    def __init__(self, name, composition: Composition, eos:str):
        self.name = name
        self.composition = composition
        self.eos = eos

    