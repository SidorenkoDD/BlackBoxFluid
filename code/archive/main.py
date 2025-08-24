from CompositionalModel import CompositionalModel
from Composition import Composition

composition = Composition({'C1': 0.5, 'C16':0.5}, c6_plus_bips_correlation=None,
                       c6_plus_correlations={'critical_temperature': 'nokey',
                        'critical_pressure' : 'rizari_daubert',
                        'acentric_factor': 'Edmister',
                        'critical_volume': 'hall_yarborough',
                        'k_watson': 'k_watson',
                        'shift_parameter': 'jhaveri_youngren'})

print(composition.composition)
print(composition.show_composition_dataframes())

model = CompositionalModel(composition, 5, 50)