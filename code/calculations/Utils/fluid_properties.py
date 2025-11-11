'''Module doc
'''
from calculations.VLE.PhaseEquilibrium import PhaseEquilibrium
from calculations.Utils.JsonDBReader import JsonDBReader

class FluidProperties:
    '''Class for calculation fluid properties'''
    def __init__(self, p, t, equil_obj: PhaseEquilibrium):
        jsondbreader = JsonDBReader()
        self.db = jsondbreader.load_database()
        self.equil_obj = equil_obj
        self.p = p
        self.t = t

    # Метод расчета молекулярной массы
    ## Для расчета молекулярной массы газовой фазы
    @property
    def molecular_mass_vapour(self):
        '''property
        returns MW of vapour phase'''
        m_to_sum = []
        for component in self.equil_obj.yi_v.keys():
            m_to_sum.append(self.equil_obj.yi_v[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)


    # Метод расчета молекулярной массы
    ## Для расчета молекулярной массы жидкой фазы
    @property
    def molecular_mass_liquid(self):
        '''property
        returns MW of liquid phase'''
        m_to_sum = []
        for component in self.equil_obj.xi_l.keys():
            m_to_sum.append(self.equil_obj.xi_l[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)

    # Методы расчета объема
    ## Расчет объема для газовой фазы
    @property
    def vapour_volume(self):
        '''property
        returns volume of vapour phase'''
        return self.equil_obj.fv * ((8.314 * self.t * self.equil_obj.eos_vapour.z / (self.p)) -
                                    self.equil_obj.eos_vapour.shift_parametr)

    ## Расчет объема для жидкой фазы
    @property
    def liquid_volume(self):
        '''property
        returns volume of liquid phase'''
        return (1 - self.equil_obj.fv) * ((8.314 * self.t *self.equil_obj.eos_liquid.z / (self.p)) -
                                          self.equil_obj.eos_liquid.shift_parametr)


    # Методы расчета плотности
    ## Расчет плотности для газовой фазы
    @property
    def vapour_density(self):
        '''property
        returns density of vapour phase'''
        return self.molecular_mass_vapour * self.equil_obj.fv / self.vapour_volume


    ## Расчет плотности для жидкой фазы
    @property
    def liquid_density(self):
        '''property
        returns density of liquid phase'''
        return self.molecular_mass_liquid * (1 - self.equil_obj.fv) / self.liquid_volume


    def calc_all_properties(self):
        '''method calculates all properties
        returns: dict
        '''
        result_dict = {'MW_vapour': self.molecular_mass_vapour,
                        'MW_liquid': self.molecular_mass_liquid,
                       'V_vapour': self.vapour_volume, 'V_liquid': self.liquid_volume,
                       'Den_vapour': self.vapour_density, 'Den_liquid': self.liquid_density}
        return result_dict

class OnePhaseProperties:
    def __init__(self, phase_stability_obj: TwoPhaseStabilityTest,):
        self.phase_stability_obj = phase_stability_obj
        jsondbreader = JsonDBReader()
        self.db = jsondbreader.load_database()
        self.p = self.phase_stability_obj.p
        self.t = self.phase_stability_obj.t


    @property
    def molecular_mass_one_phase(self):
        '''property
        returns MW of one phase'''
        m_to_sum = []
        for component in self.phase_stability_obj.composition.keys():
            m_to_sum.append(self.phase_stability_obj.composition[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)
    
    @property
    def volume_one_phase(self):
        '''property
        returns volume of vapour phase'''
        return ((CONSTANT_R * self.t * self.phase_stability_obj.vapour_z / (self.p)))
    
    @property
    def density(self):
        return self.molecular_mass_one_phase/self.volume_one_phase