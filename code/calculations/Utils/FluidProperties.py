from calculations.VLE.PhaseEquilibrium import PhaseEquilibrium
from calculations.Utils.JsonDBReader import JsonDBReader
import json


class FluidProperties:
    
    
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
        m_to_sum = []
        for component in self.equil_obj.yi_v.keys():
            m_to_sum.append(self.equil_obj.yi_v[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)


    # Метод расчета молекулярной массы
    ## Для расчета молекулярной массы жидкой фазы
    @property
    def molecular_mass_liquid(self):
        m_to_sum = []
        for component in self.equil_obj.xi_l.keys():
            m_to_sum.append(self.equil_obj.xi_l[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)
    

    # Методы расчета объема
    ## Расчет объема для газовой фазы
    @property
    def vapour_volume(self):
        print(self.equil_obj.fv)
        print(self.t)
        print(self.p)
        print(self.equil_obj.eos_vapour.z)
        print(self.equil_obj.eos_vapour.shift_parametr)
        return self.equil_obj.fv * ((8.314 * self.t * self.equil_obj.eos_vapour.z / (self.p)) - self.equil_obj.eos_vapour.shift_parametr)
    

    ## Расчет объема для жидкой фазы
    @property
    def liquid_volume(self):
        return (1 - self.equil_obj.fv) * ((8.314 * self.t *self.equil_obj.eos_liquid.z / (self.p)) - self.equil_obj.eos_liquid.shift_parametr)


    # Методы расчета плотности
    ## Расчет плотности для газовой фазы
    @property
    def vapour_density(self):
        return self.molecular_mass_vapour * self.equil_obj.fv / self.vapour_volume


    ## Расчет плотности для жидкой фазы
    @property
    def liquid_density(self):
        return self.molecular_mass_liquid * (1 - self.equil_obj.fv) / self.liquid_volume


    def calc_all_properties(self):
        result_dict = {'MW_vapour': self.molecular_mass_vapour, 'MW_liquid': self.molecular_mass_liquid, 'V_vapour': self.vapour_volume, 'V_liquid': self.liquid_volume,
                       'Den_vapour': self.vapour_density, 'Den_liquid': self.liquid_density}
        return result_dict
    


if __name__ == '__main__':
    ...