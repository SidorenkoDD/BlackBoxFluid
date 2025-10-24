'''Adapter module for Composition and calculations'''
from calculations.Composition.Composition import Composition2


class CompositionToCoreAdapter:
    '''Adapter for Composition and calculation core'''
    def __init__(self, composition_object: Composition2):
        self.composition_object = composition_object

    def transform_data_to_json(self):
        '''Transforms DataFrame to dictonary'''
        dictonary = self.composition_object._properties.to_dict()

        dictonary['bips'] = self.composition_object.bips.to_dict()
        
        return dictonary



