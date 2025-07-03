from Composition import Composition
from Conditions import Conditions
from EOS_PR_v2 import EOS_PR
from PhaseStability_v3 import PhaseStability
from PhaseEquilibrium import PhaseEquilibrium
from FluidProperties import FluidProperties


class CompositionalModel:

    def __init__(self, zi: dict, p, t):
        composition = Composition(zi)
        conditions = Conditions(p, t)

        self.phase_stability = PhaseStability(composition.composition, conditions.p, conditions.t)

        # Развилка по условию стабильности/нестабильности системы
        if self.phase_stability.stable == True:
            print('Stable')
        # Если система нестабильна, то передаем К из анализа стабильности и запускаем расчет flash
        else:

            if (self.phase_stability.S_l > 1) and (self.phase_stability.S_v > 1):
                if self.phase_stability.S_l > self.phase_stability.S_v:
                    self.phase_equilibrium = PhaseEquilibrium(composition.composition, conditions.p,
                                                               conditions.t, self.phase_stability.k_values_liquid)
                else:
                    self.phase_equilibrium = PhaseEquilibrium(composition.composition, conditions.p,
                                                               conditions.t, self.phase_stability.k_values_vapour )
                    
            if (self.phase_stability.S_v > 1) and (self.phase_stability.S_l < 1):
                self.phase_equilibrium = PhaseEquilibrium(composition.composition, conditions.p,
                                                               conditions.t, self.phase_stability.k_values_vapour )
            
            if (self.phase_stability.S_v < 1) and (self.phase_stability.S_l > 1):
                self.phase_equilibrium = PhaseEquilibrium(composition.composition, conditions.p,
                                                               conditions.t, self.phase_stability.k_values_liquid)
                
            self.phase_equilibrium.find_solve_loop()



        






if __name__ == '__main__':
    comp_model = CompositionalModel({'C2': 0.6, 'C3': 0.1,  'C6':0.3}, 2, 70)
    print(comp_model.phase_stability.stable)


    print(comp_model.phase_equilibrium.find_solve_loop())
