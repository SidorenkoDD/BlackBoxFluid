from calculations.Composition.Composition import Composition


class LBC:
    def __init__(self, param_set: dict = {'alpha0' : 0.1023,
                                          'alpha1' : 0.023364,
                                          'alpha2' : 0.058533,
                                          'alpha3' : -0.040758,
                                          'alpha4' : 0.0093324}):
        self.param_set = param_set

    