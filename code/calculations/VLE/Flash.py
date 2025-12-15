from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.VLE.PhaseEquilibrium import PhaseEquilibrium
from calculations.Utils.fluid_properties import FluidProperties, OnePhaseProperties
from calculations.Utils.BaseClasses import Calculator
from calculations.Utils.Results import TwoPhaseFlashResults
from calculations.Utils.Viscosity import LBC
from calculations.EOS.PenelouxVolumeCorrection import PenelouxVolumeCorrection

class FlashFactory:

    def __init__(self, composition, eos, viscosity_method = 'LBC'):
        self.composition = composition
        self.eos = eos
        self.viscosity_method = viscosity_method

    def create_flash(self, flash_type):
        if flash_type == 'TwoPhaseFlash':
            return TwoPhaseFlash(composition=self.composition,
                                 eos = self.eos)
        raise ValueError(f'Unknown flash: {flash_type}')


class TwoPhaseFlash(Calculator):
    def __init__(self, composition, eos, viscosity_method = 'LBC'):
        self.composition = composition
        self.eos = eos
        self.viscosity_method = viscosity_method
        self._conditions = None
        self.phase_stability = None
        self.phase_equilibrium = None
        self.fluid_properties = None

    def calculate(self, conditions):
        self._conditions = conditions
        self.phase_stability = TwoPhaseStabilityTest(self.composition, self._conditions.p,
                                                     self._conditions.t, self.eos)
        self.phase_stability.calculate_phase_stability()
        # Развилка по условию стабильности/нестабильности системы
        if self.phase_stability.stable is True:

            one_phase_props = OnePhaseProperties(self.phase_stability)

            results = TwoPhaseFlashResults(temperature=self._conditions.t,
                                           pressure= self._conditions.p,
                                           stable=self.phase_stability.stable,
                                           EOS= str(self.eos),
                                           Fv= None,
                                           Fl= None,
                                           Ki= None,

                                           liquid_composition=self.phase_stability.xi_l,
                                           vapour_composition= self.phase_stability.yi_v,
                                           liquid_z= self.phase_stability.liquid_eos.z,
                                           vapour_z= self.phase_stability.vapour_eos.z,

                                           vapour_molecular_mass= one_phase_props.molecular_mass_one_phase,
                                           liquid_molecular_mass= one_phase_props.molecular_mass_one_phase,
                                           vapour_volume= one_phase_props.volume_one_phase,
                                           liquid_volume= one_phase_props.volume_one_phase,
                                           vapour_density= one_phase_props.density,
                                           liquid_density= one_phase_props.density,
                                           liquid_viscosity = None,
                                           vapour_viscosity = None)



        # Если система нестабильна, то передаем К из анализа стабильности и запускаем расчет flash
        else:

            if (self.phase_stability.S_l > 1) and (self.phase_stability.S_v > 1):
                if self.phase_stability.S_l > self.phase_stability.S_v:
                    self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t,
                                                               self.phase_stability.k_values_liquid,
                                                               self.eos)
                    self.phase_equilibrium.find_solve_loop()
                else:
                    self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t,
                                                               self.phase_stability.k_values_vapour,
                                                               self.eos)
                    self.phase_equilibrium.find_solve_loop()
            if self.phase_stability.S_l < 1 < self.phase_stability.S_v:
                self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t,
                                                               self.phase_stability.k_values_vapour,
                                                               self.eos)
                self.phase_equilibrium.find_solve_loop()
            if self.phase_stability.S_v < 1 < self.phase_stability.S_l:
                self.phase_equilibrium = PhaseEquilibrium(self.composition, self._conditions.p,
                                                               self._conditions.t,
                                                               self.phase_stability.k_values_liquid,
                                                               self.eos)
                self.phase_equilibrium.find_solve_loop()
            self.phase_equilibrium.find_solve_loop()

            print(self.phase_equilibrium.eos_liquid.z)
            # self.phase_equilibrium.eos_vapour.calc_eos_with_peneloux_correction()
            # self.phase_equilibrium.eos_liquid.calc_eos_with_peneloux_correction()
            print(self.phase_equilibrium.eos_liquid.z)
            # pen_vol_corr = PenelouxVolumeCorrection(self.phase_equilibrium.xi_l, 
            #                                         self.composition._composition_data, 
            #                                         p = self._conditions.p,
            #                                         t = self._conditions.t)

            # pen_vol_corr_vap = PenelouxVolumeCorrection(self.phase_equilibrium.yi_v, 
            #                                         self.composition._composition_data, 
            #                                         p = self._conditions.p,
            #                                         t = self._conditions.t)

            self.fluid_properties = FluidProperties(self._conditions.p, self._conditions.t,
                                                    equil_obj= self.phase_equilibrium)

            self.viscosity_liquid = LBC(mole_fractions = self.phase_equilibrium.xi_l,
                                        composition_data = self.composition._composition_data,
                                        phase_density = self.fluid_properties.liquid_density,
                                        mw = self.fluid_properties.molecular_mass_liquid,
                                        temperature = self._conditions.t).calculate()
            
            self.viscosity_gas = LBC(mole_fractions = self.phase_equilibrium.yi_v,
                                        composition_data = self.composition._composition_data,
                                        phase_density = self.fluid_properties.vapour_density,
                                        mw = self.fluid_properties.molecular_mass_vapour,
                                        temperature = self._conditions.t).calculate()

            results = TwoPhaseFlashResults(temperature = self._conditions.t,
                                pressure = self._conditions.p,
                                EOS = str(self.eos),
                                stable = self.phase_stability.stable,
                                Fv = self.phase_equilibrium.fv,
                                Fl = (1 - self.phase_equilibrium.fv),
                                Ki = self.phase_equilibrium.k_values,
                                liquid_composition = self.phase_equilibrium.xi_l,
                                vapour_composition = self.phase_equilibrium.yi_v,
                                liquid_z = self.phase_equilibrium.eos_liquid.z,
                                vapour_z = self.phase_equilibrium.eos_vapour.z,
                                liquid_molecular_mass = self.fluid_properties.molecular_mass_liquid,
                                vapour_molecular_mass = self.fluid_properties.molecular_mass_vapour,
                                vapour_volume = self.fluid_properties.vapour_volume,
                                liquid_volume = self.fluid_properties.liquid_volume,
                                vapour_density = self.fluid_properties.vapour_density,
                                liquid_density = self.fluid_properties.liquid_density,
                                liquid_viscosity = self.viscosity_liquid,
                                vapour_viscosity = self.viscosity_gas)

        return results
