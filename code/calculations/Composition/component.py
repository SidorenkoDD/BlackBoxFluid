'''Class defines the component and it's properties'''

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
    * _check_component_in_db
    * _calculate_properties
    * set_property_value


    Errors
    ------
    * NoComponentInDBError - component doesn't found in db
    * InvalidMolarFraction - molar_fraction out of range (0,1]
    * 

    '''

    def __init__(self, component_name, mole_fraction, corr_set  = {}):
        self.component_name = component_name
        self.mole_fraction = mole_fraction
        self.corr_set = corr_set
