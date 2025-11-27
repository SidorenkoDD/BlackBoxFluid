from abc import ABC, abstractmethod
import pandas as pd
from calculations.Utils.Results import TwoPhaseFlashResults, SeparatorTestResults, StandardSeparationResults, DLEResults


class ResultsViewer(ABC):

    @abstractmethod
    def view(self):
        ...


class FlashResultsViewer(ResultsViewer):

    def view(self, dataclass_obj:TwoPhaseFlashResults):
        util_data = [dataclass_obj.pressure,
                     dataclass_obj.temperature,
                     dataclass_obj.stable,
                     dataclass_obj.EOS,
                     dataclass_obj.Fv,
                     dataclass_obj.Fl]
        util_df = pd.DataFrame(util_data, index = ['Pressure',
                                                   'Temperature',
                                                   'Stable',
                                                   'EOS',
                                                   'Fv',
                                                   'Fl'])


        composition_df = pd.DataFrame({'Component': list(dataclass_obj.vapour_composition.keys()),
                                        'Vapour':list(dataclass_obj.vapour_composition.values()),
                                        'Liquid':list(dataclass_obj.liquid_composition.values()),
                                        'Ki': list(dataclass_obj.Ki.values())
                                        })
        composition_df[['Vapour', 'Liquid']] = composition_df[['Vapour', 'Liquid']] * 100

        phase_props_df = pd.DataFrame({'Vapour': [dataclass_obj.vapour_z,
                                                  dataclass_obj.vapour_molecular_mass,
                                                  dataclass_obj.vapour_volume,
                                                  dataclass_obj.vapour_density,
                                                  dataclass_obj.vapour_viscosity],

                                       'Liquid':[dataclass_obj.liquid_z,
                                                 dataclass_obj.liquid_molecular_mass,
                                                 dataclass_obj.liquid_volume,
                                                 dataclass_obj.liquid_density,
                                                 dataclass_obj.liquid_viscosity]},

                                       index= ['Z', 'MW', 'Vol', 'Dens', 'Visc'])
        
        print(util_df)
        print('====')
        print(composition_df)
        print('====')
        print(phase_props_df)


class SeparatorTestResultsViewer(ResultsViewer):
    '''Class to view separator test results in dataframes'''
    def view(self, separator_test_results : SeparatorTestResults):

        stages_pressure = [separator_test_results.first_stage_pressure,
                           separator_test_results.second_stage_pressure,
                           separator_test_results.third_stage_pressure]
        stages_temperature = [separator_test_results.first_stage_temperature,
                              separator_test_results.second_stage_temperature,
                              separator_test_results.third_stage_temperature]
        
        stages_info_df = pd.DataFrame([stages_pressure, stages_temperature],
                                   index= ['Pressure', 'Temperature'],
                                   columns= ['I', 'II', 'III'])

        gas_composition_df = pd.DataFrame({'I': list(separator_test_results.first_stage_vapour_composition.values()),
                                           'II': list(separator_test_results.second_stage_vapour_composition.values()),
                                           'III': list(separator_test_results.third_stage_vapour_composition.values())},
                                           index= list(separator_test_results.first_stage_vapour_composition.keys()))
        
        liquid_composition_df = pd.DataFrame({'I': list(separator_test_results.first_stage_liquid_composition.values()),
                                           'II': list(separator_test_results.second_stage_liquid_composition.values()),
                                           'III': list(separator_test_results.third_stage_liquid_composition.values())},
                                           index= list(separator_test_results.first_stage_liquid_composition.keys()))

        fv = [separator_test_results.first_stage_fv,
              separator_test_results.second_stage_fv,
              separator_test_results.third_stage_fv]
        
        fl = [separator_test_results.first_stage_fl,
              separator_test_results.second_stage_fl,
              separator_test_results.third_stage_fl]

        gas_z = [separator_test_results.first_stage_vapour_z,
                 separator_test_results.second_stage_vapour_z,
                 separator_test_results.third_stage_vapour_z]

        liquid_z = [separator_test_results.first_stage_liquid_z,
                    separator_test_results.second_stage_liquid_z,
                    separator_test_results.third_stage_liquid_z]
        
        gas_mw = [separator_test_results.first_stage_vapour_mw,
                  separator_test_results.second_stage_vapour_mw,
                  separator_test_results.third_stage_vapour_mw]
        
        liquid_mw = [separator_test_results.first_stage_liquid_mw,
                  separator_test_results.second_stage_liquid_mw,
                  separator_test_results.third_stage_liquid_mw]
        
        gas_volume = [separator_test_results.first_stage_vapour_volume,
                      separator_test_results.second_stage_vapour_volume,
                      separator_test_results.third_stage_vapour_volume]
        
        liquid_volume = [separator_test_results.first_stage_liquid_volume,
                         separator_test_results.second_stage_liquid_volume,
                         separator_test_results.third_stage_liquid_volume]
        
        gas_density = [separator_test_results.first_stage_vapour_density,
                       separator_test_results.second_stage_vapour_density,
                       separator_test_results.third_stage_vapour_density]
        
        liquid_density = [separator_test_results.first_stage_liquid_density,
                          separator_test_results.second_stage_liquid_density,
                          separator_test_results.third_stage_liquid_density]
        
        fv_by_stages_df = pd.DataFrame([fv, fl],
                                       index=['Fv', 'Fl'],
                                       columns= ['I', 'II', 'III'])

        phase_props_df = pd.DataFrame([gas_z, liquid_z,
                                    gas_mw, liquid_mw,
                                    gas_volume, liquid_volume,
                                    gas_density, liquid_density],
                                   index= ['Gas Z', 'Liquid Z',
                                           'Gas MW', 'Liquid MW',
                                           'Gas Volume', 'Liquid Volume',
                                           'Gas Density', 'Liquid Density'],
                                   columns= ['I', 'II', 'III'])
        print('STAGES')
        print(stages_info_df)
        print('=====')
        print('FV AND FL BY STAGES')
        print(fv_by_stages_df)
        print('=====')
        print('PHASE PROPERTIES BY STAGES')
        print(phase_props_df)
        print('=====')
        print('GAS COMPOSITION BY STAGES')
        print(gas_composition_df)
        print('=====')
        print('LIQUID COMPOSITION BY STAGES')
        print(liquid_composition_df)


class StandardSeparationResultsViewer(ResultsViewer):
    def view(self, standard_separation_results: StandardSeparationResults):
        presure_arr = [standard_separation_results.p_res,
                       standard_separation_results.p_sat,
                       standard_separation_results.p_stc]
        temperature_arr = [standard_separation_results.t_res,
                           standard_separation_results.t_res,
                           20]
        liquid_density_arr = [standard_separation_results.liquid_density_p_res,
                              standard_separation_results.liquid_density_p_sat,
                              standard_separation_results.liquid_density_separated]
        bo_arr = [standard_separation_results.bo_p_res,
                  standard_separation_results.bo_p_sat,
                  None]
        rs_arr = [standard_separation_results.rs,
                  standard_separation_results.rs,
                  0]

        primary_output_df = pd.DataFrame({'Pressure' : presure_arr,
                                          'Temperature' : temperature_arr,
                                          'Liquid density' : liquid_density_arr,
                                          'Bo' : bo_arr,
                                          'Rs' : rs_arr})
        primary_output_df.index = ['Pres', 'Psat', 'STC']
        return primary_output_df

class DLEResultsViewer(ResultsViewer):
    def view(self, dle_results: DLEResults):
        primary_output_df = pd.DataFrame({'Index' : dle_results.index,
                                          'Pressure': dle_results.pressure_arr,
                                          'Temperature' : dle_results.temperature_arr,
                                          'Fl' : dle_results.fl_arr,
                                          'Fv' : dle_results.fv_arr,
                                          'Liquid Z' : dle_results.liquid_z,
                                          'Gas Z' : dle_results.gas_z,
                                          'Liquid volume' : dle_results.liquid_volume_arr,
                                          'Gas volume' : dle_results.gas_volume_arr,
                                          'Liquid density' : dle_results.liquid_density_arr,
                                          'Gas density' : dle_results.gas_density_arr,
                                           'Bo' : dle_results.bo,
                                           'Rs' : dle_results.rs,
                                           'Liquid viscosity' : dle_results.liquid_viscosity,
                                           'Gas viscosity' : dle_results.gas_viscosity})
        #primary_output_df['Rs'] = primary_output_df['Rs'][::-1].values
        return primary_output_df
    
    def view_liquid_compositions(self, dle_results : DLEResults):
        liquid_compositions_df = pd.DataFrame.from_dict(data = dle_results.liquid_compositions).T
        liquid_compositions_df.columns = dle_results.index
        liquid_compositions_df = liquid_compositions_df * 100
        return liquid_compositions_df

    def view_gas_compositions(self, dle_results : DLEResults):
        gas_compositions_df = pd.DataFrame.from_dict(data = dle_results.gas_compositions).T
        gas_compositions_df.columns = dle_results.index
        gas_compositions_df = gas_compositions_df * 100
        return gas_compositions_df