from component import Component


def test(component):
    obj = Component(component_name=component, mole_fraction=1)
    obj.component_properties_df
    obj.set_property_value('critical_temperature', 1)
    obj.component_properties_df


if __name__ == '__main__':
    test('C3')
    test('C45')

