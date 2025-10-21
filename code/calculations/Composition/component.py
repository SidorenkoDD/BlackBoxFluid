'''Class defines the component and it's properties'''
from pathlib import Path
import sys
import re

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
    * component_name - name of component for connetion to db : str
    * mole_fraction : float
    * corr_set : default is: ... ,dict

    Methods
    -------
    * _create_component_db
    * _calculate_properties
    * set_property_value

    Errors
    ------
    * NoComponentError - component doesn't found in db
    * InvalidMolarFractionError - molar_fraction out of range (0,1]
    *

    '''

    def __init__(self, component_name, mole_fraction,
                 corr_set  = {'critical_temperature': 'Kesler_Lee',
                              'critical_pressure' : 'rizari_daubert',
                              'acentric_factor': 'Edmister',
                              'critical_volume': 'hall_yarborough',
                              'k_watson': 'k_watson',
                              'shift_parameter': 'jhaveri_youngren'}):
        
        self._component_name = component_name
        self._mole_fraction = mole_fraction
        self._corr_set = corr_set

        self._validate_mole_fraction()
        #self._create_component_db()


    def _validate_mole_fraction(self) -> None:
        if 0 >= self._mole_fraction > 1:
            raise IndentationError(f'Invalid value for mole fraction: {self.mole_fraction}\n Must be in range (0, 1]!')

    def _check_c6_plus(self) -> bool:
        match = re.search(r'(\d+)$', self._component_name)
        value = int(match.group(1))
        if value > 6:
            return True
        return False

    def _create_component_db(self) -> dict:
        '''Method creates component properties for composition,  loading from json
        '''
        jsondbreader = JsonDBReader()
        self._component_data = jsondbreader.load_database()
        print(self._component_data)
        
        if self._check_c6_plus():
            try:
                component_properties_calculator = PlusComponentProperties(self._component_name, correlations_config = self._corr_set)
                component_properties_calculator.calculate_all_props_v2()
                self._component_data['molar_mass'][self._component_name] = component_properties_calculator.data['M']
                self._component_data['critical_pressure'][self._component_name] = component_properties_calculator.data['p_c']
                self._component_data['critical_temperature'][self._component_name] = component_properties_calculator.data['t_c']
                self._component_data['acentric_factor'][self._component_name] = component_properties_calculator.data['acentric_factor']
                self._component_data['critical_volume'][self._component_name] = component_properties_calculator.data['crit_vol']
                self._component_data['shift_parameter'][self._component_name] = component_properties_calculator.data['Cpen']
            except Exception as e:
                raise ValueError(f"Can't create composition: no component {self._component_name} in DB!")
        else:
            ...


    def set_property_value(prop, value):
        ...
