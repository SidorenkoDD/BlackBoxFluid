# import pandas as pd

from Composition import Composition
from FlashFactory import FlashFactory
from Flash import FlashFasade
from Conditions import Conditions



class CompositionalModel:
    def __init__(self,zi: Composition, eos: str = 'PREOS', flash = 'TwoPhaseFlash'):
        self.composition = zi
        self.eos = eos
        self.flash_name = flash
        self.flash = FlashFasade(self.composition, self.eos)
        

    def calculate_flash(self,conditions):
        self.flash.calculate_flash(conditions=conditions)
        


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




    comp_model = CompositionalModel(comp, eos = 'SRKEOS')

    conditions = Conditions(6, 50)

    

    flash_2_phase = comp_model.flash.TwoPhaseFlash.calculate_flash(conditions)
    flash_2_phase.show_results()

    



    

    



    




    