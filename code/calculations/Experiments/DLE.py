from calculations.Experiments.BaseExperiment import PVTExperiment
from calculations.Composition.Composition import Composition
from calculations.VLE.flash import FlashFactory
from calculations.Utils.Conditions import Conditions
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation
from calculations.Utils.Results import DLEResults
import numpy as np

class DLE(PVTExperiment):
    def __init__(self, composition, eos):
        self._composition = composition
        self._eos = eos
        self.result = {}
        self.fl = []

    def calculate(self, temperature : float, pressure_list : list | None = None,
                   n_steps : float = 10, flash_type = 'TwoPhaseFlash'):
        pb_obj = SaturationPressureCalculation(self._composition,p_max=40, temp= temperature)
        pb = pb_obj.sp_convergence_loop(self._eos)

        if pressure_list is None:
            pressure_array = np.linspace(pb, 0.1, n_steps)
            print(pressure_array)
            print(pressure_array[1:])
            flash_object = FlashFactory(self._composition, self._eos)
            flash_calculator = flash_object.create_flash(flash_type= flash_type)
            #расчет для первого значения давления
            first_step_conditions = Conditions(pressure_array[0], temperature)
            self.result[f'{first_step_conditions.p}_{first_step_conditions.t}'] = flash_calculator.calculate(conditions=first_step_conditions)
            # создаем атрибут состав, который далее будем менять
            self.liquid_composition_dict = self.result[f'{first_step_conditions.p}_{first_step_conditions.t}'].liquid_composition
            
            # создаем атрибут доля жидкости, который далее будет меняться по ступеням
            self.fl.append(self.result[f'{first_step_conditions.p}_{first_step_conditions.t}'].Fl)

            for pressure in pressure_array[1:]:
                print(self.liquid_composition_dict)
                self.liquid_composition = Composition(self.liquid_composition_dict)
                self.liquid_composition._composition_data = self._composition._composition_data
                self._flash_object = FlashFactory(self.liquid_composition, self._eos)
                flash_calculator = self._flash_object.create_flash(flash_type = flash_type)
                current_conditions = Conditions(pressure, temperature)
                self.result[f'{current_conditions.p}_{current_conditions.t}']= flash_calculator.calculate(conditions = current_conditions)
                self.fl.append(self.result[f'{current_conditions.p}_{current_conditions.t}'].Fl)
                self.liquid_composition_dict = self.result[f'{current_conditions.p}_{current_conditions.t}'].liquid_composition

            self.liquid_composition_last_stage = Composition(self.liquid_composition_dict)
            self.liquid_composition_last_stage._composition_data = self._composition._composition_data
            print(self.liquid_composition_last_stage._composition)
            flash_object = FlashFactory(self.liquid_composition_last_stage, self._eos)
            flash_calculator = flash_object.create_flash(flash_type= flash_type)
            #расчет для стандартных условий (последняя ступень)
            last_step_conditions = Conditions(0.101325, 20)
            self.result[f'STC_{last_step_conditions.p}_{last_step_conditions.t}'] = flash_calculator.calculate(conditions=last_step_conditions)

        else:
            ...

class DLE_2(PVTExperiment):
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

    def _calculate_rs(self, gas_vol, fv_arr):
        fv_arr = [1 if x is None else x for x in fv_arr]
        corrected_vol = []
        cumulative_product = 1
        
        for i in range(len(fv_arr)):
            corrected_vol.append(gas_vol[i] * cumulative_product)
            cumulative_product *= fv_arr[i]
        return corrected_vol / self.oil_residual_volume


    def calculate(self, p_resirvoir, reservoir_temperature : float,
                  pressure_by_stages : list,
                  flash_type = 'TwoPhaseFlash'):


        def _is_strictly_descending() -> None:
            '''Method checks descending values for pressure_list'''
            if all(pressure_by_stages[i] < pressure_by_stages[i-1] for i in range(1, len(pressure_by_stages))) is False:
                pressure_by_stages.sort(reverse=True)
            else:
                pass

        def _is_p_sat_in_pressure_by_stages_list() -> list:
            '''Method checks is p_sat in list, if no, append p_sat in list'''
            pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= reservoir_temperature)
            pb = pb_obj.sp_convergence_loop(self._eos)
            if pb not in pressure_by_stages:
                pb_obj = SaturationPressureCalculation(self._composition,p_max=50, temp= reservoir_temperature)
                pb = pb_obj.sp_convergence_loop(self._eos)
                pressure_by_stages.append(pb)
                pressure_by_stages.sort(reverse=True)
            else:
                pass

        def _is_p_res_in_pressure_by_stages_list() -> list:
            '''Method checks is p_res in list, in no, append p_res in list'''
            if p_resirvoir in pressure_by_stages:
                pass
            else:
                pressure_by_stages.append(p_resirvoir)
                pressure_by_stages.sort(reverse=True)

        _is_strictly_descending()
        _is_p_res_in_pressure_by_stages_list()
        _is_p_sat_in_pressure_by_stages_list()
        # calculate first step (p res)
        flash_object = FlashFactory(self._composition, self._eos)
        flash_calculator = flash_object.create_flash(flash_type= flash_type)
        first_step_conditions = Conditions(pressure_by_stages[0], reservoir_temperature)
        self._result_dict[f'{first_step_conditions.p}_{first_step_conditions.t}'] = flash_calculator.calculate(conditions=first_step_conditions)

        self.liquid_composition_dict = self._result_dict[f'{first_step_conditions.p}_{first_step_conditions.t}'].liquid_composition
        self.fl.append(self._result_dict[f'{first_step_conditions.p}_{first_step_conditions.t}'].Fl)
        # calculate from p sat to p = 1 atm, Tres
        for pressure in pressure_by_stages[1:]:
            self.liquid_composition = Composition(self.liquid_composition_dict)
            self.liquid_composition._composition_data = self._composition._composition_data
            self._flash_object = FlashFactory(self.liquid_composition, self._eos)
            flash_calculator = self._flash_object.create_flash(flash_type = flash_type)
            current_conditions = Conditions(pressure, reservoir_temperature)
            self._result_dict[f'{current_conditions.p}_{current_conditions.t}']= flash_calculator.calculate(conditions = current_conditions)
            self.fl.append(self._result_dict[f'{current_conditions.p}_{current_conditions.t}'].Fl)
            self.liquid_composition_dict = self._result_dict[f'{current_conditions.p}_{current_conditions.t}'].liquid_composition

        # calculate stc
        self.liquid_composition = Composition(self.liquid_composition_dict)
        self.liquid_composition._composition_data = self._composition._composition_data
        last_step_conditions = Conditions(0.101325, 20)
        self._flash_object = FlashFactory(self.liquid_composition, self._eos)
        flash_calculator = self._flash_object.create_flash(flash_type = flash_type)
        self._result_dict[f'STC_{last_step_conditions.p}_{last_step_conditions.t}'] = flash_calculator.calculate(conditions=last_step_conditions)
        self.bo = self._calculate_bo(liq_vol = [self._result_dict[stage].liquid_volume for stage in list(self._result_dict.keys())],
                                     fl_arr = [self._result_dict[stage].Fl for stage in list(self._result_dict.keys())])
        self.rs = self._calculate_rs(gas_vol = [self._result_dict[stage].vapour_volume for stage in list(self._result_dict.keys())],
                                     fv_arr = [self._result_dict[stage].Fv for stage in list(self._result_dict.keys())])

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
                                 gas_compositions = [self._result_dict[stage].vapour_composition for stage in list(self._result_dict.keys())],)
                                 #bo = [None] + list(self._calculate_bo(liq_vol = [self._result_dict[stage].liquid_volume for stage in list(self._result_dict.keys())],
                                 #                        fl_arr = [self._result_dict[stage].Fl for stage in list(self._result_dict.keys())])))

        return self.result
    
