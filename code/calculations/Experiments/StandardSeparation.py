from calculations.VLE.flash import FlashFactory
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Utils.Conditions import Conditions


class StandardSeparation(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self._reservoir_flash_result = None
        self._stc_flash_result = None
        self._liquid_volume_res = None
        self._liquid_volume_stc = None
        self._gas_vol_stc = None


    def _calculate_bo(self):
        self._liquid_volume_res = self._reservoir_flash_result.liquid_volume
        self._liquid_volume_stc = self._stc_flash_result.liquid_volume
        return self._liquid_volume_res / self._liquid_volume_stc

    def _calcluate_rs(self):
        self._gas_vol_stc = self._stc_flash_result.vapour_volume
        return self._gas_vol_stc / self._liquid_volume_stc

    def calculate(self, p_res: float, t_res:float, flash_type = 'TwoPhaseFlash'):
        self._flash_object = FlashFactory(self._composition, self._eos)
        self._standard_conditions = Conditions(p_res, t_res)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._reservoir_flash_result = flash_calculator.calculate(conditions=self._standard_conditions)

        self._flash_object = FlashFactory(self._composition, self._eos)
        self._standard_conditions = Conditions(0.101325, 20)
        flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
        self._stc_flash_result = flash_calculator.calculate(conditions=self._standard_conditions)

        self._bo = self._calculate_bo()

    @property
    def show_results(self):
        ...