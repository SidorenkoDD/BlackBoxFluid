'''Class defines the component and it's properties'''

from pathlib import Path
import sys
import re
import pandas as pd
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from calculations.Utils.Errors import NoComponentError, InvalidMolarFractionError
from calculations.Utils.JsonDBReader import JsonDBReader
from calculations.Composition.PlusComponentCorrelations import PlusComponentProperties


class Component:
    '''
    Component object

    Attributes
    ----------
    * _component_name : name of component for connetion to db:str
    * _mole_fraction : float
    * _corr_set : default is: {
                              'critical_temperature': 'pedersen',

                              'critical_pressure' :'rizari_daubert',

                              'acentric_factor':'Edmister',

                              'critical_volume':'hall_yarborough',

                              'k_watson':'k_watson',

                              'shift_parameter': 'jhaveri_youngren'} :dict

    * _component_properties - component properties
    * _db - connector to json db

    Methods
    -------
    * _validate_mole_fraction
    * _check_c5_plus
    * _create_component_db
    * _calculate_properties
    * set_property_value

    * _get_component_name
    * _get_component_data
    * _get_component_mole_fraction
    * component_properties_df


    Errors
    ------
    * NoComponentError - component doesn't found in db
    * InvalidMolarFractionError - molar_fraction out of range (0,1]
    *
    '''

    def __init__(self, component_name, mole_fraction,
                 corr_set  = {'critical_temperature': 'pedersen',
                              'critical_pressure' : 'rizari_daubert',
                              'acentric_factor': 'Edmister',
                              'critical_volume': 'hall_yarborough',
                              'k_watson': 'k_watson',
                              'shift_parameter': 'jhaveri_youngren'}):

        self._component_name = component_name
        self._mole_fraction = mole_fraction
        self._corr_set = corr_set
        self._component_properties = {}
        self._db = None

        self._validate_mole_fraction()
        self._create_component_db()


    def _validate_mole_fraction(self) -> None:
        '''Method validates mole fraction of component'''
        if (self._mole_fraction <= 0) or (self._mole_fraction > 1) :
            raise InvalidMolarFractionError(f'Invalid value for mole fraction: {self._mole_fraction}\n Must be in range (0, 1]!')

    def _check_c5_plus(self) -> bool:
        '''Method checks if component is C6+ component'''
        ##TODO: Crashes if component name doesn't end with number
        match = re.search(r'(\d+)$', self._component_name)
        value = int(match.group(1))
        if value > 5:
            return True
        return False

    def _create_component_db(self) -> dict:
        '''Method creates component properties for composition,  loading from json
        '''
        jsondbreader = JsonDBReader()
        self._db = jsondbreader.load_database()

        if self._check_c5_plus():
            try:
                component_properties_calculator = PlusComponentProperties(self._component_name,
                                                                          correlations_config = self._corr_set)
                component_properties_calculator.calculate_all_props_v2()
                self._component_properties['mole_fraction'] = self._mole_fraction
                self._component_properties['molar_mass'] = self._db['molar_mass'][self._component_name]
                self._component_properties['gamma'] = self._db['gamma'][self._component_name]
                self._component_properties['Tb'] = self._db['Tb'][self._component_name]
                self._component_properties['critical_pressure'] = component_properties_calculator.data['p_c']
                self._component_properties['Pc corr'] = self._corr_set['critical_pressure']
                self._component_properties['critical_temperature'] = component_properties_calculator.data['t_c']
                self._component_properties['Tc_corr'] = self._corr_set['critical_temperature']
                self._component_properties['acentric_factor'] = component_properties_calculator.data['acentric_factor']
                self._component_properties['Acf_corr'] = self._corr_set['acentric_factor']
                self._component_properties['critical_volume'] = component_properties_calculator.data['crit_vol']
                self._component_properties['Vc_corr'] = self._corr_set['critical_volume']
                self._component_properties['shift_parameter'] = component_properties_calculator.data['Cpen']
                self._component_properties['Cpen_corr'] = self._corr_set['shift_parameter']
                self._component_properties['K_Watson'] = component_properties_calculator.data['Kw']
                self._component_properties['Data Source'] = 'correlation'

            except KeyError as e:
                raise NoComponentError(f'No component {self._component_name} in database!', e)
        else:
            try:
                self._component_properties['mole_fraction'] = self._mole_fraction
                self._component_properties['molar_mass'] = self._db['molar_mass'][self._component_name]
                self._component_properties['gamma'] = self._db['gamma'][self._component_name]
                self._component_properties['Tb'] = self._db['Tb'][self._component_name]
                self._component_properties['critical_pressure'] = self._db['critical_pressure'][self._component_name]
                self._component_properties['Pc corr'] = 'DB'
                self._component_properties['critical_temperature'] = self._db['critical_temperature'][self._component_name]
                self._component_properties['Tc_corr'] = 'DB'
                self._component_properties['acentric_factor'] = self._db['acentric_factor'][self._component_name]
                self._component_properties['Acf_corr'] = 'DB'
                self._component_properties['critical_volume'] = self._db['critical_volume'][self._component_name]
                self._component_properties['Vc_corr'] = 'DB'
                self._component_properties['shift_parameter'] = self._db['shift_parameter'][self._component_name]
                self._component_properties['Cpen_corr'] = 'DB'
                self._component_properties['K_Watson'] = 'None'
                self._component_properties['Data Source'] = 'json database'
            except KeyError as e:
                raise NoComponentError(f'No component {self._component_name} in database!', e)

    def set_property_value(self, prop, value) -> None:
        '''Method allows to change component property
        
        Args
        ----
        * prop - property to change
        * value - value to set
        '''
        self._component_properties[prop] = value

    @property
    def _get_component_name(self):
        '''property returns name of component'''
        return self._component_name

    @property
    def _get_component_data(self):
        '''property returns DataFrame with all component properties'''
        return pd.DataFrame.from_dict([self._component_properties])

    @property
    def _get_component_mole_fraction(self):
        return self._mole_fraction

    @property
    def component_properties_df(self):
        '''Property returns dataframe with component properties'''
        print('=====')
        print(f'COMPONENT "{self._component_name}" PROPERTIES:')
        print(pd.DataFrame.from_dict([self._component_properties]))
        print('=====')