from PhaseStability_v3 import PhaseStability
from PhaseEquilibrium import PhaseEquilibrium
from FluidProperties import FluidProperties

import pandas as pd
from abc import abstractmethod, ABC
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




class Flash(ABC):
    def __init__(self, composition):

        self.composition = composition

    
    @abstractmethod
    def calculate_flash(self):
        ...


class FlashFasade:
    def __init__(self, composition):
        self.composition = composition

    # def __dir__(self):
    #     return ['TwoPhaseFlash', 'FourPhaseFlash']
    
    @property
    def TwoPhaseFlash(self):
        return TwoPhaseFlash(self.composition)
    
    @property
    def FourPhaseFlash(self):
        return TwoPhaseFlash(self.composition)


class TwoPhaseFlash(Flash):
    
    def __init__(self, composition, eos: str):
        self.composition = composition



    def calculate_flash(self, conditions):
        
        self._conditions = conditions

        self.phase_stability = PhaseStability(self.composition, self._conditions.p, self._conditions.t)

        # Развилка по условию стабильности/нестабильности системы
        if self.phase_stability.stable == True:
            print('Stable')
            print(self.phase_stability.S_v, self.phase_stability.S_l)
            print(self.phase_stability.trivial_solution_vapour, self.phase_stability.trivial_solution_liquid)
        # Если система нестабильна, то передаем К из анализа стабильности и запускаем расчет flash
        else:

            if (self.phase_stability.S_l > 1) and (self.phase_stability.S_v > 1):
                if self.phase_stability.S_l > self.phase_stability.S_v:
                    self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_liquid)
                else:
                    self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_vapour )
                    
            if (self.phase_stability.S_v > 1) and (self.phase_stability.S_l < 1):
                self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_vapour )
            
            if (self.phase_stability.S_v < 1) and (self.phase_stability.S_l > 1):
                self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_liquid)
                
            self.phase_equilibrium.find_solve_loop()

            



            self.fluid_properties = FluidProperties(self._conditions.p, self._conditions.t, equil_obj= self.phase_equilibrium)

            self.results = CompositionalResults(self.phase_stability.stable,
                self.phase_equilibrium.yi_v, self.phase_equilibrium.xi_l, 
                                                self.phase_equilibrium.fv, self.phase_equilibrium.k_values, 
                                                self.phase_equilibrium.eos_vapour.choosen_eos_root, 
                                                  self.phase_equilibrium.eos_liquid.choosen_eos_root, 
                                                self.fluid_properties.molecular_mass_vapour, 
                                                self.fluid_properties.molecular_mass_liquid, 
                                                self.fluid_properties.vapour_volume, self.fluid_properties.liquid_volume, 
                                                self.fluid_properties.vapour_density, self.fluid_properties.liquid_density)
            print(self.results)


    def show_results(self):
        
            yi_vapour_df = pd.DataFrame.from_dict(self.results.yi_vapour, orient= 'index')
            xi_liquid_df = pd.DataFrame.from_dict(self.results.xi_liquid, orient= 'index')
            ki = pd.DataFrame.from_dict(self.results.Ki, orient= 'index')
            flash_results = pd.DataFrame({'Stable': self.results.stable, 'Fv': self.results.fv,
                                        'Z':[self.results.z_vapour, self.results.z_liquid],
                                            'MW': [self.results.MW_liquid, self.results.MW_liquid], 
                                        'Dens': [self.results.density_vapour,  self.results.density_liquid]})
            print('COMP DATA')
            print(self.composition.show_composition_dataframes())
            print('=====')
            print(f'FLASH RESULTS: P {self._conditions.p}, T: {self._conditions.t}')
            print('Gas composition')
            print(yi_vapour_df.to_markdown())
            print('=====')
            print('Liquid composition')
            print(xi_liquid_df.to_markdown())
            print('=====')
            print(flash_results.to_markdown())
            print('=====')
            print('Ki')
            print(ki.to_markdown())
            print('=====')