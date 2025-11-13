from calculations.VLE.flash import FlashFactory
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Utils.Conditions import Conditions
from calculations.Utils.Results import StandardSeparationResults
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation


class StandardSeparation(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self._reservoir_flash_result = None
        self._stc_flash_result = None
        self._liquid_volume_res = None
        self._liquid_volume_stc = None
        self._gas_vol_stc = None


    def _calculate_bo_p_res(self):
        self._liquid_volume_res = self._reservoir_flash_result.liquid_volume
        self._liquid_volume_stc = self._stc_flash_result.liquid_volume
        return self._liquid_volume_res / self._liquid_volume_stc
    
    def _calculate_bo_p_sat(self):
        self._liquid_volume_sat = self._saturation_flash_result.liquid_volume
        self._liquid_volume_stc = self._stc_flash_result.liquid_volume
        return self._liquid_volume_sat / self._liquid_volume_stc

    def _calcluate_rs(self):
        self._gas_vol_stc = self._stc_flash_result.vapour_volume
        return self._gas_vol_stc / self._liquid_volume_stc


    def calculate(self, p_res: float, t_res:float, flash_type = 'TwoPhaseFlash'):
        pb_obj = SaturationPressureCalculation(self._composition,p_max= 40, temp= t_res)
        pb = pb_obj.sp_convergence_loop(self._eos)

        self._flash_object = FlashFactory(self._composition, self._eos)
        self._reservoir_conditions = Conditions(p_res, t_res)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._reservoir_flash_result = flash_calculator.calculate(conditions=self._reservoir_conditions)

        self._flash_object = FlashFactory(self._composition, self._eos)
        self._saturation_conditions = Conditions(pb, t_res)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._saturation_flash_result = flash_calculator.calculate(conditions=self._saturation_conditions)

        self._flash_object = FlashFactory(self._composition, self._eos)
        self._standard_conditions = Conditions(0.101325, 20)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._stc_flash_result = flash_calculator.calculate(conditions=self._standard_conditions)


        self._result = StandardSeparationResults( p_res = p_res,
                                           p_sat = pb,
                                           p_stc = 0.101325,
                                           t_res = t_res,
                                           liquid_density_p_res = self._reservoir_flash_result.liquid_density,
                                           liquid_density_p_sat = self._saturation_flash_result.liquid_density,
                                           liquid_density_separated = self._stc_flash_result.liquid_density,
                                           bo_p_res = self._calculate_bo_p_res(),
                                           bo_p_sat = self._calculate_bo_p_sat(),
                                           separated_gas_dens= self._stc_flash_result.vapour_density,
                                           rs = self._calcluate_rs()
                                           )
        return self._result
    

    @property
    def show_results(self):
        ...