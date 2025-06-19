import yaml
import math
from logger import LogManager
from EOS_PR_v2 import EOS_PR

logger = LogManager(__name__)


class PhaseStability:

    def __init__(self, zi: dict, p: float, t: float):
        
        # инициализируем состав
        self.zi = zi
        
        # инициализируем термобарику
        if __name__ == '__main__':
            self.p = p * math.pow(10,5)
            self.t = t + 273.14
        
        else:
            self.p = p
            self.t = t

        # Подключение к yaml-файлику
        try:
            with open('code/db.yaml', 'r') as db_file:
                self.db = yaml.safe_load(db_file)
            logger.log.debug('Данные компонент из .yaml прочитаны успешно') 

        except Exception as e:
            logger.log.fatal('Данные компонент не найдены!', e)


    # Расчет начального УРС
    def calc_initial_eos(self):
        initial_eos = EOS_PR(self.zi, self.p, self.t)
        return initial_eos


    # Расчет начальных констант равновесия по уравнению Вильсона
    ## Начальные константы равновесия одинаковы для жидкой и газовой фазы
    def calc_initial_k_values_wilson(self):
        k_initial = {}
        for component in list(self.zi.keys()):
            k_initial[component] = (math.pow(math.e, 5.37 * (1 + self.db['acentric_factor'][component]) * (1 - (self.db['critical_temperature'][component]/self.t))) / 
                                    (self.p / self.db['critical_pressure'][component]))
            
        return k_initial
    

    # Расчет мольных долей в газовой фазе
    def calc_Yi_v(self, zi: dict, k_values: dict):
        Yi_v = {}
        for component in list(zi.values()):
            Yi_v[component] = zi[component] * k_values[component]

        return Yi_v


    # Расчет мольных долей в жидкой фазе
    def calc_Xi_l(self, zi: dict, k_values: dict):
        Xi_l = {}
        for component in list(zi.values()):
            Xi_l[component] = zi[component] / k_values[component]
        
        return Xi_l


    # Расчет суммы мольных долей в газовой фазе
    def calc_sum_Yi_v(self, Yi_v:dict):
        return sum(list(Yi_v.values()))
    

    # Расчет суммы мольных долей в жидкой фазе
    def calc_sum_Xi_l(self, Xi_l:dict):
        return sum(list(Xi_l.values()))
    

    # Нормируем мольные доли газовой фазы
    def normalize_mole_fractions_vapour(self, Yi_v, S_v):

    def    