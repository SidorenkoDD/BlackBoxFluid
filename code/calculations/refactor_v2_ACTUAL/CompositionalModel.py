# import pandas as pd

from Composition import Composition
from FlashFactory import FlashFactory
from Flash import FlashFasade
from Conditions import Conditions



class CompositionalModel:
    def __init__(self,zi: Composition, eos: str = 'PREOS', flash_type = 'TwoPhaseFlash'):
        self.composition = zi
        self.eos = eos
        self.flash_name = flash_type
        self.flash = FlashFasade(self.composition, self.eos)
    

    # def calculate_flash(self,conditions):
    #     self.flash.calculate_flash(conditions=conditions)
        


if __name__ == '__main__':


    comp = Composition({'C1': 0.5, 'C3': 0.4,  'C9':0.1},
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'kesler_lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'Edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'}
                       )




    comp_model = CompositionalModel(comp, eos = 'PREOS')

    conditions = Conditions(0.1, 50)

    comp_model.flash.TwoPhaseFlash.calculate_flash(conditions)

    # comp_model.flash.calculate_flash(conditions)
    # comp_model.flash.show_results()

    



    

    



    




    