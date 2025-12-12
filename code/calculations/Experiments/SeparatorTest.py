from calculations.Composition.Composition import Composition
from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Utils.Errors import LenthMissMatchError, nStagesError
from calculations.Utils.Conditions import Conditions, StandardConditions
from calculations.Utils.Results import SeparatorTestResults, DLEResults
from calculations.VLE.flash import FlashFactory
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation
from itertools import accumulate
import pandas as pd


class SeparatorTest(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self.result = {}

    def check_stages(self, stages_pressure, stages_temperature):
        if len(stages_pressure) != len(stages_temperature):
            raise LenthMissMatchError(f'{stages_pressure} and {stages_temperature} are different length!')


    def calculate(self, stages_pressure: list, stages_temperature: list, flash_type = 'TwoPhaseFlash'):
        if len(stages_pressure) != len(stages_temperature):
            raise LenthMissMatchError(f'{stages_pressure} and {stages_temperature} are different length!')
        else:
            for i, stage_pressure in enumerate(stages_pressure):
                self._flash_object = FlashFactory(self._composition, self._eos)
                self._standard_conditions = Conditions(stage_pressure, stages_temperature[i])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.result[f"Stage {i+1}"] = flash_calculator.calculate(conditions=self._standard_conditions)

    def calculate_3stages(self, stages_pressure: list, stages_temperature: list, flash_type = 'TwoPhaseFlash'):
        if len(stages_pressure) != len(stages_temperature):
            raise LenthMissMatchError(f'{stages_pressure} and {stages_temperature} are different length!')
        elif (len(stages_pressure) != 3) or  (len(stages_temperature) != 3):
            raise nStagesError('This method allows to calculate 3 stages only!')

        else:
                # Здесь расчет первой ступени
                self._flash_object = FlashFactory(self._composition, self._eos)
                self.first_stage_conditions = Conditions(stages_pressure[0], stages_temperature[0])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.first_stage_result = flash_calculator.calculate(conditions=self.first_stage_conditions)

                # Начинаем расчет второй ступени
                self.second_stage_composition = Composition(self.first_stage_result.liquid_composition)
                self.second_stage_composition._composition_data = self._composition._composition_data
                self._flash_object = FlashFactory(self.second_stage_composition, self._eos)
                self.second_stage_conditions = Conditions(stages_pressure[1], stages_temperature[1])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.second_stage_result = flash_calculator.calculate(conditions=self.second_stage_conditions)

                # Расчет третьей ступени
                self.third_stage_composition = Composition(self.second_stage_result.liquid_composition)
                self.third_stage_composition._composition_data = self._composition._composition_data
                self._flash_object = FlashFactory(self.third_stage_composition, self._eos)
                self.third_stage_conditions = Conditions(stages_pressure[2], stages_temperature[2])
                flash_calculator = self._flash_object.create_flash(flash_type= flash_type)
                self.third_stage_result = flash_calculator.calculate(conditions=self.third_stage_conditions)


        self.result = SeparatorTestResults(first_stage_pressure = self.first_stage_conditions.p,
                                      first_stage_temperature = self.first_stage_conditions.t,
                                      first_stage_fv = self.first_stage_result.Fv,
                                      first_stage_fl = self.first_stage_result.Fl,
                                      first_stage_vapour_composition = self.first_stage_result.vapour_composition,
                                      first_stage_liquid_composition = self.first_stage_result.liquid_composition,
                                      first_stage_liquid_z = self.first_stage_result.liquid_z,
                                      first_stage_vapour_z = self.first_stage_result.vapour_z,
                                      first_stage_k_values = self.first_stage_result.Ki,
                                      first_stage_vapour_mw = self.first_stage_result.vapour_molecular_mass,
                                      first_stage_liquid_mw = self.first_stage_result.liquid_molecular_mass,
                                      first_stage_vapour_volume = self.first_stage_result.vapour_volume,
                                      first_stage_liquid_volume = self.first_stage_result.liquid_volume,
                                      first_stage_vapour_density = self.first_stage_result.vapour_density,
                                      first_stage_liquid_density = self.first_stage_result.liquid_density,
                                    
                                      second_stage_pressure = self.second_stage_conditions.p,
                                      second_stage_temperature = self.second_stage_conditions.t,
                                      second_stage_fv = self.second_stage_result.Fv,
                                      second_stage_fl = self.second_stage_result.Fl,
                                      second_stage_vapour_composition = self.second_stage_result.vapour_composition,
                                      second_stage_liquid_composition = self.second_stage_result.liquid_composition,
                                      second_stage_liquid_z = self.second_stage_result.liquid_z,
                                      second_stage_vapour_z = self.second_stage_result.vapour_z,
                                      second_stage_k_values = self.second_stage_result.Ki,
                                      second_stage_vapour_mw = self.second_stage_result.vapour_molecular_mass,
                                      second_stage_liquid_mw = self.second_stage_result.liquid_molecular_mass,
                                      second_stage_vapour_volume = self.second_stage_result.vapour_volume,
                                      second_stage_liquid_volume = self.second_stage_result.liquid_volume,
                                      second_stage_vapour_density = self.second_stage_result.vapour_density,
                                      second_stage_liquid_density = self.second_stage_result.liquid_density,

                                      third_stage_pressure = self.third_stage_conditions.p,
                                      third_stage_temperature = self.third_stage_conditions.t,
                                      third_stage_fv = self.third_stage_result.Fv,
                                      third_stage_fl = self.third_stage_result.Fl,
                                      third_stage_vapour_composition = self.third_stage_result.vapour_composition,
                                      third_stage_liquid_composition = self.third_stage_result.liquid_composition,
                                      third_stage_liquid_z = self.third_stage_result.liquid_z,
                                      third_stage_vapour_z = self.third_stage_result.vapour_z,
                                      third_stage_k_values = self.third_stage_result.Ki,
                                      third_stage_vapour_mw = self.third_stage_result.vapour_molecular_mass,
                                      third_stage_liquid_mw = self.third_stage_result.liquid_molecular_mass,
                                      third_stage_vapour_volume = self.third_stage_result.vapour_volume,
                                      third_stage_liquid_volume = self.third_stage_result.liquid_volume,
                                      third_stage_vapour_density = self.third_stage_result.vapour_density,
                                      third_stage_liquid_density = self.third_stage_result.liquid_density)

        return self.result

    @property
    def gas_compositions(self):
        return pd.DataFrame({f'First Stage\n P:{self.first_stage_conditions.p}, T {self.first_stage_conditions.t}': self.result.first_stage_vapour_composition,
                             f'Second Stage\n P:{self.second_stage_conditions.p}, T {self.second_stage_conditions.t}': self.result.second_stage_vapour_composition,
                             f'Third Stage\n P:{self.third_stage_conditions.p}, T {self.third_stage_conditions.t}': self.result.third_stage_vapour_composition,})
    

class SeparatorTestModifiedDLE(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self.fl = []
        self._result_dict = {}

    def _calculate_bo(self, liq_vol, fl_arr):

        fl_arr = [1 if x is None else x for x in fl_arr]
        corrected_vol = []
        cumulative_product = 1
        for i in range(len(fl_arr)):
            corrected_vol.append(liq_vol[i] * cumulative_product)
            cumulative_product *= fl_arr[i]
        self.oil_residual_volume = corrected_vol[-1]
        return corrected_vol / corrected_vol[-1]

    def _gas_vol_to_stc(self, p_stage, t_stage, z_stage, v_stage, z_stc):
        return p_stage * v_stage * z_stc * 293.14 / (0.101325 * z_stage * t_stage)
    
    def _calculate_rs(self, p_arr, z_arr, t_arr, gas_vol_arr, fl_arr, p_sat):
        # 1. first step : calculate Vgas with Fl correction
        fl_arr = [1 if x is None else x for x in fl_arr]
        corrected_vol_fl = []
        cumulative_product = 1
        for i in range(len(fl_arr)):
            corrected_vol_fl.append(gas_vol_arr[i] * cumulative_product)
            cumulative_product *= fl_arr[i]

        # 2. second step : convert gas vol to stc. 
        ## There are two ways: calc with the use of EOS, or calc with flash to STC
        gas_vol_stc_arr = []
        for i in range(len(gas_vol_arr)):
            gas_vol_stc_arr.append(self._gas_vol_to_stc(p_stage = p_arr[i],
                                                        t_stage = t_arr[i],
                                                        z_stage = z_arr[i],
                                                        v_stage = corrected_vol_fl[i],
                                                        z_stc = z_arr[-1]))

        # 3. third step : make gas vol 0 for p >= p_sat and for last stage
        gas_vol_stc_arr = [0 if p_arr[i] >= p_sat else gas_vol_stc_arr[i] for i in range(len(p_arr))]
        gas_vol_stc_arr[-1] = 0
        print(f'GVOL BY STAGES STC: {gas_vol_stc_arr}')
        # 4. fourth step : calc acc sum of gas volume by stages
        cumulative_sum = list(accumulate(gas_vol_stc_arr))
        print(f'GVOL BY STAGES ACC STC: {cumulative_sum}')
        # 5. revert gvol
        gas_stc_acc_reverted = []
        for i in range(len(cumulative_sum)):
            gas_stc_acc_reverted.append(cumulative_sum[-1] - cumulative_sum[i])
        
        return gas_stc_acc_reverted / self.oil_residual_volume


    # NOT USED
    def calculate_g_vol_stc_by_stages_with_droplet(self, gas_compositions_arr, flash_type = 'TwoPhaseFlash') -> list:
        g_vol_stc_arr = []
        for composition in gas_compositions_arr:
            self.gas_composition = Composition(composition)
            self.liquid_composition._composition_data = self._composition._composition_data

            flash_object = FlashFactory(self.gas_composition, self._eos)
            flash_calculator = flash_object.create_flash(flash_type= flash_type)
            stc_conditions = Conditions(0.101325, 20)
            flash_result_stc = flash_calculator.calculate(conditions = stc_conditions)
            g_vol_stc_arr.append(flash_result_stc.liquid_volume + flash_result_stc.vapour_volume)
    
        return g_vol_stc_arr


    def calculate(self, reservoir_pressure : float,
                  reservoir_temperature : float,
                  pressure_by_stages : list,
                  temperature_by_stages : list,
                  flash_type = 'TwoPhaseFlash'):
        pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= reservoir_temperature)
        self.pb = pb_obj.sp_convergence_loop(self._eos)

        def _is_strictly_descending() -> None:
            '''Method checks descending values for pressure_list'''
            if all(pressure_by_stages[i] < pressure_by_stages[i-1] for i in range(1, len(pressure_by_stages))) is False:
                pressure_by_stages.sort(reverse=True)
            else:
                pass

        def _is_p_sat_in_pressure_by_stages_list() -> list:
            '''Method checks is p_sat in list, if no, append p_sat in list'''
            if self.pb not in pressure_by_stages:
                pressure_by_stages.append(self.pb)
                pressure_by_stages.sort(reverse=True)
            else:
                pass

        def _is_p_res_in_pressure_by_stages_list() -> list:
            '''Method checks is p_res in list, in no, append p_res in list'''
            if reservoir_pressure in pressure_by_stages:
                pass
            else:
                pressure_by_stages.append(reservoir_pressure)
                pressure_by_stages.sort(reverse=True)

        def _is_t_res_in_temperature_by_stages_list() -> list:
            '''Method checks is p_res in list, in no, append p_res in list'''
            if reservoir_temperature in temperature_by_stages:
                pass
            else:
                temperature_by_stages.append(reservoir_temperature)
                temperature_by_stages.sort(reverse=True)

        _is_strictly_descending()
        _is_p_res_in_pressure_by_stages_list()
        _is_p_sat_in_pressure_by_stages_list()
        _is_t_res_in_temperature_by_stages_list()


        # calculate first step (p res)
        flash_object = FlashFactory(self._composition, self._eos)
        flash_calculator = flash_object.create_flash(flash_type= flash_type)
        first_step_conditions = Conditions(pressure_by_stages[0], reservoir_temperature)
        self._result_dict[f'{first_step_conditions.p}_{first_step_conditions.t}'] = flash_calculator.calculate(conditions=first_step_conditions)
        self.liquid_composition_dict = self._result_dict[f'{first_step_conditions.p}_{first_step_conditions.t}'].liquid_composition
        self.fl.append(self._result_dict[f'{first_step_conditions.p}_{first_step_conditions.t}'].Fl)

        # calculate from p sat to p = 1 atm, Tres
        for i, pressure in enumerate(pressure_by_stages[1:]):
            self.liquid_composition = Composition(self.liquid_composition_dict)
            self.liquid_composition._composition_data = self._composition._composition_data
            self._flash_object = FlashFactory(self.liquid_composition, self._eos)
            flash_calculator = self._flash_object.create_flash(flash_type = flash_type)
            current_conditions = Conditions(pressure, temperature_by_stages[i])
            self._result_dict[f'{current_conditions.p}_{current_conditions.t}']= flash_calculator.calculate(conditions = current_conditions)
            self.fl.append(self._result_dict[f'{current_conditions.p}_{current_conditions.t}'].Fl)
            self.liquid_composition_dict = self._result_dict[f'{current_conditions.p}_{current_conditions.t}'].liquid_composition

        # calculate stc
        self.liquid_composition = Composition(self.liquid_composition_dict)
        self.liquid_composition._composition_data = self._composition._composition_data
        last_step_conditions = StandardConditions()
        self._flash_object = FlashFactory(self.liquid_composition, self._eos)
        flash_calculator = self._flash_object.create_flash(flash_type = flash_type)
        self._result_dict[f'STC_{last_step_conditions.p}_{last_step_conditions.t}'] = flash_calculator.calculate(conditions=last_step_conditions)

        # calculate bo and rs
        self.bo = self._calculate_bo(liq_vol = [self._result_dict[stage].liquid_volume for stage in list(self._result_dict.keys())],
                                     fl_arr = [self._result_dict[stage].Fl for stage in list(self._result_dict.keys())])
        self.rs = self._calculate_rs(p_arr = [self._result_dict[stage].pressure for stage in list(self._result_dict.keys())],
                                     z_arr = [self._result_dict[stage].vapour_z for stage in list(self._result_dict.keys())],
                                     t_arr = [self._result_dict[stage].temperature for stage in list(self._result_dict.keys())],
                                     gas_vol_arr = [self._result_dict[stage].vapour_volume for stage in list(self._result_dict.keys())],
                                     fl_arr = [self._result_dict[stage].Fl for stage in list(self._result_dict.keys())],
                                     p_sat = self.pb)

        self.result = DLEResults(index = list(self._result_dict.keys()),
                                 pressure_arr = [self._result_dict[stage].pressure for stage in list(self._result_dict.keys())],
                                 temperature_arr = [self._result_dict[stage].temperature for stage in list(self._result_dict.keys())],
                                 liquid_volume_arr = [self._result_dict[stage].liquid_volume for stage in list(self._result_dict.keys())],
                                 fl_arr = [self._result_dict[stage].Fl for stage in list(self._result_dict.keys())],
                                 fv_arr = [self._result_dict[stage].Fv for stage in list(self._result_dict.keys())],
                                 gas_volume_arr = [self._result_dict[stage].vapour_volume for stage in list(self._result_dict.keys())],
                                 liquid_density_arr = [self._result_dict[stage].liquid_density for stage in list(self._result_dict.keys())],
                                 gas_density_arr = [self._result_dict[stage].vapour_density for stage in list(self._result_dict.keys())],
                                 liquid_z = [self._result_dict[stage].liquid_z for stage in list(self._result_dict.keys())],
                                 gas_z = [self._result_dict[stage].vapour_z for stage in list(self._result_dict.keys())],
                                 liquid_compositions = [self._result_dict[stage].liquid_composition for stage in list(self._result_dict.keys())],
                                 gas_compositions = [self._result_dict[stage].vapour_composition for stage in list(self._result_dict.keys())],
                                 liquid_viscosity= None,
                                 gas_viscosity = None,
                                 bo = self.bo,
                                 rs = self.rs)
        

        return self.result
