# import pandas as pd

from calculations.Composition.Composition import Composition
from calculations.VLE.Flash import Flash as flash
from calculations.Utils.Conditions import Conditions
#import Flash as flash
#from Conditions import Conditions



class CompositionalModel:
    def __init__(self,zi: Composition):
        self.composition = zi
        self.flash = flash.FlashFasade(self.composition)
    

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
    
    comp_model = CompositionalModel(comp)

    conditions = Conditions(6, 50)


    flash1 = comp_model.flash.ForPhaseFlash
    
    flash1.calculate_flash(conditions=conditions)

    flash1.show_results()
    




    