from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.VLE.PhaseEquilibrium import PhaseEquilibrium
from calculations.Utils.FluidProperties import FluidProperties
from calculations.Utils.BaseClasses import Calculator
from calculations.Utils.Results import TwoPhaseFlashResults





class FlashFactory:

    def __init__(self, composition, eos):
        self.composition = composition
        self.eos = eos
    
    # @staticmethod
    def create_flash(self, flash_type):
        if flash_type == 'TwoPhaseFlash':
            return TwoPhaseFlash(composition=self.composition, eos = self.eos)
        else:
            raise ValueError(f'Unknown flash: {flash_type}')
        

class TwoPhaseFlash(Calculator):
    
    def __init__(self, composition, eos):
        self.composition = composition
        self.eos = eos


    def calculate(self, conditions):
        
        self._conditions = conditions

        self.phase_stability = TwoPhaseStabilityTest(self.composition, self._conditions.p, self._conditions.t, self.eos)
        self.phase_stability.calculate_phase_stability()

        # Развилка по условию стабильности/нестабильности системы
        if self.phase_stability.stable == True:


            results = TwoPhaseFlashResults(temperature=self._conditions.t,
                                           pressure= self._conditions.p,
                                           stable=self.phase_stability.stable,
                                           EOS= str(self.eos),
                                           Fv= None,
                                           Ki= None,
                                           liquid_composition=None,
                                           vapour_composition= None,
                                           liquid_z= None, 
                                           vapour_z= None,
                                           vapour_molecular_mass= None,
                                           liquid_molecular_mass= None,
                                           vapour_volume= None,
                                           liquid_volume= None,
                                           vapour_density= None,
                                           liquid_density= None)



        # Если система нестабильна, то передаем К из анализа стабильности и запускаем расчет flash
        else:

            if (self.phase_stability.S_l > 1) and (self.phase_stability.S_v > 1):
                if self.phase_stability.S_l > self.phase_stability.S_v:
                    self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_liquid, self.eos)
                    self.phase_equilibrium.find_solve_loop()
                else:
                    self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_vapour, self.eos)
                    self.phase_equilibrium.find_solve_loop()
                    
            if (self.phase_stability.S_v > 1) and (self.phase_stability.S_l < 1):
                self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_vapour, self.eos)
                self.phase_equilibrium.find_solve_loop()
            
            if (self.phase_stability.S_v < 1) and (self.phase_stability.S_l > 1):
                self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t, self.phase_stability.k_values_liquid, self.eos)
                self.phase_equilibrium.find_solve_loop()
                
            self.phase_equilibrium.find_solve_loop()

            



            self.fluid_properties = FluidProperties(self._conditions.p, self._conditions.t, equil_obj= self.phase_equilibrium)


            results = TwoPhaseFlashResults(temperature = self._conditions.t,
                                           pressure = self._conditions.p,
                                           EOS= str(self.eos),
                                           stable= self.phase_stability.stable,
                                           Fv= self.phase_equilibrium.fv,
                                           Fl = (1 - self.phase_equilibrium.fv),
                                           Ki= self.phase_equilibrium.k_values,
                                           liquid_composition= self.phase_equilibrium.xi_l,
                                           vapour_composition= self.phase_equilibrium.yi_v,
                                           liquid_z= self.phase_equilibrium.eos_liquid.z,
                                           vapour_z=self.phase_equilibrium.eos_vapour.z,
                                           liquid_molecular_mass= self.fluid_properties.molecular_mass_liquid,
                                           vapour_molecular_mass= self.fluid_properties.molecular_mass_vapour,
                                           vapour_volume= self.fluid_properties.vapour_volume,
                                           liquid_volume= self.fluid_properties.liquid_volume,
                                           vapour_density= self.fluid_properties.vapour_density,
                                           liquid_density= self.fluid_properties.liquid_density)
            


        return results
            


