from component import Component


def test(component):
    obj = Component(component_name=component, mole_fraction=0.5)
    print(obj._check_c6_plus())
    obj._create_component_db()
    print(obj._component_data.keys())


if __name__ == '__main__':
    test('C7')
    