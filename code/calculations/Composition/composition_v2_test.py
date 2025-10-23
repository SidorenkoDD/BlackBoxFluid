from Composition import Composition2
from component import Component
def composition_test():
    component_obj1 = Component('C1',0.2)
    component_obj6 = Component('C6',0.2)
    component_obj2 = Component('C9', 0.2)
    composition_obj3 = Component('C13', 0.2)
    composition_obj4 = Component('C14', 0.2)
    composition_obj = Composition2([component_obj1, component_obj2, composition_obj3, composition_obj4, component_obj6])
    composition_obj._create_composition_df()
    print(composition_obj.composition_data)
    print(composition_obj.composition_bips)


if __name__ == '__main__':
    composition_test()