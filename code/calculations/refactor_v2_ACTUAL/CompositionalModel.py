from Composition import Composition
from FlashFactory import FlashFactory
from Flash import FlashFasade
from Conditions import Conditions



class CompositionalModel:
    def __init__(self,zi: Composition, eos: str = 'PREOS', flash_type = 'TwoPhaseFlash'):
        self.composition = zi
        self.eos = eos
        self.flash_type = flash_type
        self.flash_fasade = FlashFasade(self.composition, self.eos)

        self.flash_results = {}

    def flash(self, conditions, flash_type = 'TwoPhaseFlash'):
        flash_calculator = getattr(self.flash_fasade, flash_type)
        result = flash_calculator.calculate(conditions)
        self.flash_results[str(flash_type) + '_' + str(conditions.p)+'_' + str(conditions.t)] = result 
    


if __name__ == '__main__':


    comp = Composition({'C1': 0.35, 'C2':0.15, 'C3': 0.1, 'C6': 0.05, 'iC4': 0.1,'C8':0.05, 'C9':0.05, 'C10': 0.05, 'C11': 0.05, 'C16':0.05},
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'pedersen',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'}
                       )

    comp.show_composition_dataframes()



    comp_model = CompositionalModel(comp, eos = 'PREOS')

    conditions1 = Conditions(5, 30)
    #conditions2 = Conditions(7,50)

    comp_model.flash(conditions=conditions1)
    print(comp_model.flash_results)
    #comp_model.flash(conditions=conditions2)
    #print(comp_model.flash_results.keys())


    



    

    



    




    