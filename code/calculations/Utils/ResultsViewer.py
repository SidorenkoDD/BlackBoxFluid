from abc import ABC, abstractmethod
import pandas as pd


class ResultsViewer(ABC):

    @abstractmethod
    def view(self):
        ...


class FlashResultsViewer(ResultsViewer):

    def view(self, dataclass_obj):
        util_data = [dataclass_obj.pressure, dataclass_obj.temperature, dataclass_obj.stable, dataclass_obj.EOS, dataclass_obj.Fv, dataclass_obj.Fl]
        util_df = pd.DataFrame(util_data, index = ['Pressure', 'Temperature', 'Stable', 'EOS', 'Fv', 'Fl'])


        composition_df = pd.DataFrame({'Component': list(dataclass_obj.vapour_composition.keys()),
                                        'Vapour':list(dataclass_obj.vapour_composition.values()),
                                        'Liquid':list(dataclass_obj.liquid_composition.values()),
                                        'Ki': list(dataclass_obj.Ki.values())
                                        })
        composition_df[['Vapour', 'Liquid']] = composition_df[['Vapour', 'Liquid']] * 100

        phase_props_df = pd.DataFrame({'Vapour': [dataclass_obj.vapour_z, dataclass_obj.vapour_molecular_mass, dataclass_obj.vapour_volume, dataclass_obj.vapour_density],
                                       'Liquid':[dataclass_obj.liquid_z, dataclass_obj.liquid_molecular_mass, dataclass_obj.liquid_volume, dataclass_obj.liquid_density]},
                                       index= ['Z', 'MW', 'Vol', 'Dens'])
        
        print(util_df)
        print('====')
        print(composition_df)
        print('====')
        print(phase_props_df)