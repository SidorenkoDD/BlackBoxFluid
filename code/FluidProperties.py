from PhaseEquilibrium import PhaseEquilibrium
import yaml
class FluidProperties:
    
    
    def __init__(self, zi, p, t):
        
        self.zi = zi

        with open('code/db.yaml', 'r') as db_file:
            self.db = yaml.safe_load(db_file)
        
        
        if __name__ == '__main__':
            self.p = p
            self.t = t + 273.14

        else:
            self.p = p
            self.t = t

        self.phase_equilibrium = PhaseEquilibrium(zi= self.zi, p = self.p, t = self.t)
        self.phase_equilibrium.find_solve_loop()

        self.mm_v = self.calc_molecular_mass_vapour()
        self.mm_l = self.calc_molecular_mass_liquid()

        self.volume_v = self.calc_vapour_volume()
        self.volume_l = self.calc_liquid_volume()

        self.density_v = self.calc_vapour_density()
        self.density_l = self.calc_liquid_density()


    # Метод расчета молекулярной массы
    ## Для расчета молекулярной массы газовой фазы
    def calc_molecular_mass_vapour(self):
        m_to_sum = []
        for component in self.phase_equilibrium.yi_v.keys():
            m_to_sum.append(self.phase_equilibrium.yi_v[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)


    # Метод расчета молекулярной массы
    ## Для расчета молекулярной массы жидкой фазы
    def calc_molecular_mass_liquid(self):
        m_to_sum = []
        for component in self.phase_equilibrium.xi_l.keys():
            m_to_sum.append(self.phase_equilibrium.xi_l[component] * self.db['molar_mass'][component])
        return sum(m_to_sum)
    
    # Методы расчета объема
    ## Расчет объема для газовой фазы
    def calc_vapour_volume(self):
        return self.phase_equilibrium.fv * ((8.314 * self.t * self.phase_equilibrium.eos_vapour.choosen_eos_root/ self.p) - self.phase_equilibrium.eos_vapour.shift_parametr)

    ## Расчет объема для жидкой фазы
    def calc_liquid_volume(self):
        return (1 - self.phase_equilibrium.fv) * ((8.314 * self.t * self.phase_equilibrium.eos_liquid.choosen_eos_root/ self.p) - self.phase_equilibrium.eos_liquid.shift_parametr)
    

    # Методы расчета плотности
    ## Расчет плотности для газовой фазы
    def calc_vapour_density(self):
        return self.mm_v * self.phase_equilibrium.fv / self.volume_v
        
    ## Расчет плотности для жидкой фазы
    def calc_liquid_density(self):
        return self.mm_l * (1 - self.phase_equilibrium.fv) / self.volume_l


if __name__ == '__main__':
    props = Properties({'C1': 0.5, 'nC4':0.5}, 8, 40)
    #props.phase_equilibrium.find_solve_loop()
    print('=== Fv ===')
    print(props.phase_equilibrium.fv)
    print('=== Составы ===')
    print(props.phase_equilibrium.xi_l)
    print(props.phase_equilibrium.yi_v)
    print('=== Плотности ===')
    print(props.density_v * 1000)
    print(props.density_l * 1000)
    print('=== Молекулярные массы ===')
    print(props.mm_v)
    print(props.mm_l)
    print('=== Z факторы ===')
    print(props.phase_equilibrium.eos_vapour.choosen_eos_root)
    print(props.phase_equilibrium.eos_liquid.choosen_eos_root)