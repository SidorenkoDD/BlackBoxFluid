from pathlib import Path
import sys

# Добавляем корневую директорию в PYTHONPATH
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))


from calculations.Composition.Composition import Composition
from calculations.VLE.Flash import FlashFactory
from calculations.Utils.Conditions import Conditions
from calculations.PhaseDiagram.PhaseDiagram_v4 import PhaseDiagram



class CompositionalModel:
    def __init__(self,zi: Composition, eos: str = 'PREOS'):
        self._composition = zi
        self._eos = eos
        self._flash_results = {}

    def flash(self, conditions, flash_type = 'TwoPhaseFlash'):
        self._flash_object = FlashFactory(self._composition, self._eos)
        flash_calculator = self._flash_object.create_flash(flash_type=flash_type)
        result = flash_calculator.calculate(conditions=conditions)

        self._flash_results[str(flash_type) + '_' + str(conditions.p)+'_' + str(conditions.t)] = result 
    
    
    def plot_phase_diagram(self, p_max = 40, t_min = 0, t_max = 200, t_step = 10):
        self.phase_diagram_obj = PhaseDiagram(self.composition, p_max= p_max, t_min= t_min, t_max= t_max, t_step= t_step)
        self.phase_diagram_obj.calc_phase_diagram(eos = self.eos)
        self.phase_diagram_obj.plot_phase_diagram()


    @property
    def show_flashes(self):
        return self._flash_results


if __name__ == '__main__':


    comp = Composition({'C1': 0.35, 'C2':0.1, 'C3': 0.05, 'nC5':0.05, 'C6': 0.05, 'iC4': 0.1,'C8':0.05, 'C9':0.05, 'C10': 0.05, 'C11': 0.05, 'C16':0.05, 'C44': 0.05},
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'kesler_lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'}
                       )

    comp.show_composition_dataframes()

    #comp.edit_component_properties('C1', {'molar_mass': 0.1, 'critical_pressure': 500})

    #comp.show_composition_dataframes()

    comp_model = CompositionalModel(comp, eos = 'PREOS')

    conditions1 = Conditions(5, 50)
    # conditions2 = Conditions(7,50)

    comp_model.flash(conditions=conditions1)
    #print(comp_model.flash_results)
    
    # #comp_model.flash(conditions=conditions2)
    print(comp_model._flash_results)
    print(comp_model.show_flashes)


    



