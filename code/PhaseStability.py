from Logger import LogManager
from EOS_v2 import EOS_PR
import math as math
import yaml
logger = LogManager(__name__)


class PhaseStability:

    def __init__(self, zi:dict, p:float, t:float):
        self.zi = zi
        self.p = p
        self.t = t

        try:
    
            with open('code/db.yaml', 'r') as db_file:
                self.db = yaml.safe_load(db_file)
            logger.log.info('Данные компонент из .yaml прочитаны успешно') 

        except Exception as e:
            logger.log.fatal('Данные компонент не найдены!', e)

        self.initial_eos_solve = EOS_PR(self.zi, self.p, self.t)


    # Расчет начальных констант равновесия
        try:
            self.initial_k_values = {}
            for component in list(self.zi.keys()):
                self.initial_k_values[component] = (self.calc_k_initial(p_crit_i = self.db['critical_pressure'][component],
                                                                 t_crit_i = self.db['critical_temperature'][component],
                                                                 acentric_factor_i= self.db['acentric_factor'][component]))
            
        except Exception as e:
            logger.log.error('Начальные константы равновесия не рассчитаны', e)


        # Расчет Xi_Yi
        try:
            self.Yi_Xi = self.calc_Yi_v_and_Xi_l(zi= self.zi, k_vals= self.initial_k_values)

        except Exception as e:
            logger.log.error('Не удалось рассчитать Yi Xi', e)


        # Расчет суммы мольных долей
        try:
            self.sum_mole_fractions = self.summerize_mole_fractions(Yi_Xi= self.Yi_Xi)

        except Exception as e:
            logger.log.error('Расчет суммы мольных долей жидкой и газовой фазы не проведен', e)


        # Расчет нормализованных мольных долей в жидкости и в газе
        try:
            self.normalized_mole_fractions = self.normalize_mole_fraction(self.zi, self.Yi_Xi, self.sum_mole_fractions)

        except Exception as e:
            logger.log.error('Расчет нормализованных мольных долей не проведен', e)




    # Метод для расчета начальных констант равновесия 
    def calc_k_initial(self, p_crit_i, t_crit_i, acentric_factor_i):
        return math.pow(math.e, (5.37*(1+acentric_factor_i)*(1-(t_crit_i/self.t)))) / (self.p/p_crit_i)
    

    # Метод для расчета Yi_v и Xi_l
    ##TODO: в чем разница между К_vapour и K_liquid?
    def calc_Yi_v_and_Xi_l(self, zi:dict, k_vals):
        Yi_and_Xi = {}
        vapour = {}
        liquid = {}
        for component in list(zi.keys()):
            vapour[component] = self.zi[component] / 100 * k_vals[component]
            liquid[component] = self.zi[component] / (100 * k_vals[component])
        Yi_and_Xi['vapour'] = vapour
        Yi_and_Xi['liquid'] = liquid
        return  Yi_and_Xi

    # метод расчета суммы мольных долей
    def summerize_mole_fractions(self, Yi_Xi):
        sum_mole_fractions = {'vapour': sum(list(Yi_Xi['vapour'].values())),
                              'liquid': sum(list(Yi_Xi['liquid'].values()))}
        return sum_mole_fractions


    # Метод для нормализации мольных долей
    def normalize_mole_fraction(self, zi, Yi_Xi, sum_mole_fractions):
        normalized_mole_fractions = {}
        normalized_vapour_fractions = {}
        normalized_liquid_fractions = {}
        for component in list(zi.keys()):
            normalized_vapour_fractions[component] = round(Yi_Xi['vapour'][component] / sum_mole_fractions['vapour'] * 100, 3)

        for component in list(zi.keys()):
            normalized_liquid_fractions[component] = round(Yi_Xi['liquid'][component] / sum_mole_fractions['liquid'] * 100, 3)

        normalized_mole_fractions['vapour'] = normalized_vapour_fractions
        normalized_mole_fractions['liquid'] = normalized_liquid_fractions

        return normalized_mole_fractions

    def analyse_stability_pipeline(self):
        eos_for_liquid = EOS_PR(self.normalized_mole_fractions['liquid'], self.p, self.t)
        print(f'eos_for_liq: {eos_for_liquid.fugacity_by_roots}')
        eos_for_vapour = EOS_PR(self.normalized_mole_fractions['vapour'], self.p, self.t)
        print(f'eos_for_vap: {eos_for_vapour.fugacity_by_roots}')
        print(f'choosen_root: {eos_for_vapour.choosen_eos_root}')
        
        ri_v = []
        ri_l = []

        for component in eos_for_vapour.fugacity_by_roots[eos_for_vapour.choosen_eos_root]:
            ri_v.append(self.initial_eos_solve.fugacity_by_roots[self.initial_eos_solve.choosen_eos_root][component] / 
                        eos_for_vapour.fugacity_by_roots[eos_for_vapour.choosen_eos_root][component])
            


if __name__ == '__main__':
    phase_stability = PhaseStability({'C1':100}, p= 100, t=80)
    print(f'init_k_vals: {phase_stability.initial_k_values}')
    print(f'Yi_Xi: {phase_stability.Yi_Xi}')
    print(f'sum_mole_fractions: {phase_stability.sum_mole_fractions}')
    print(f'norm_mole_fractions: {phase_stability.normalized_mole_fractions}')
    phase_stability.analyse_stability_pipeline()

