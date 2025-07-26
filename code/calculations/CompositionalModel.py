from Composition import Composition
from Conditions import Conditions

from PhaseStability_v3 import PhaseStability
from PhaseEquilibrium import PhaseEquilibrium
from FluidProperties import FluidProperties
from dataclasses import dataclass


@dataclass 
class CompositionalResults:
    stable: bool
    yi_vapour: dict
    xi_liquid: dict
    fv: float
    Ki: dict

    z_vapour: float
    z_liquid: float

    MW_vapoour: float
    MW_liquid:float

    volume_vapour: float
    volume_liquid: float

    density_vapour: float
    density_liquid: float


class CompositionalModel:

    def __init__(self, zi: dict, p, t):
        composition = Composition(zi)
        conditions = Conditions(p, t)

        self.phase_stability = PhaseStability(composition.composition, conditions.p, conditions.t)

        # Развилка по условию стабильности/нестабильности системы
        if self.phase_stability.stable == True:
            print('Stable')
            print(self.phase_stability.S_v, self.phase_stability.S_l)
            print(self.phase_stability.trivial_solution_vapour, self.phase_stability.trivial_solution_liquid)
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



            self.fluid_properties = FluidProperties(conditions.p, conditions.t, equil_obj= self.phase_equilibrium)

            self.results = CompositionalResults(self.phase_stability.stable,
                self.phase_equilibrium.yi_v, self.phase_equilibrium.xi_l, 
                                                self.phase_equilibrium.fv, self.phase_equilibrium.k_values, 
                                                self.phase_equilibrium.eos_vapour.choosen_eos_root, 
                                                  self.phase_equilibrium.eos_liquid.choosen_eos_root, 
                                                self.fluid_properties.molecular_mass_vapour, 
                                                self.fluid_properties.molecular_mass_liquid, 
                                                self.fluid_properties.vapour_volume, self.fluid_properties.liquid_volume, 
                                                self.fluid_properties.vapour_density, self.fluid_properties.liquid_density)




if __name__ == '__main__':
    comp_model = CompositionalModel({'C1': 0.5, 'C3': 0.5}, 6, 50)
    print(comp_model.phase_stability.stable)
    print(comp_model.fluid_properties.liquid_density)


    
    print(comp_model.results)