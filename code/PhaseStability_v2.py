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
        try:
            self.initial_eos = self.calc_initial_eos()
            logger.log.debug('Начальное УРС решено')
        
        except Exception as e:
            logger.log.error('Начальное УРС не рассчитано', e)


        # Расчет начальных K-values
        try:
            self.k_values = self.calc_initial_k_values_wilson()
            logger.log.debug('Начальные константы равновесия рассчитаны')\
            
        except Exception as e:
            logger.log.error('Начальные константы равновесия не рассчитаны', e)


        # Расчет мольных долей в газовой фазе
        try:
            self.Yi_v = self.calc_Yi_v(zi = self.zi, k_values= self.k_values)
            logger.log.debug('мольные доли для газовой фазы рассичтаны')

        except Exception as e:
            logger.log.error('мольные доли для газовой фазы не рассчитаны', e)

        
        # Расчет мольных долей в жидкой фазе
        try:
            self.Xi_l = self.calc_Xi_l(zi = self.zi, k_values= self.k_values)
            logger.log.debug('мольные доли для жидкой фазы рассичтаны')

        except Exception as e:
            logger.log.error('мольные доли для жидкой фазы не рассчитаны', e)


        # Расчет суммы мольных долей для газовой фазы
        try:
            self.S_v = self.calc_S_v(Yi_v= self.Yi_v)
            logger.log.debug('Рассчитана сумма мольных долей для газовой фазы')

        except Exception as e:
            logger.log.error('Сумма мольных долей для газовой фазы не рассчитана', e)

        
        # Расчет суммы мольных долей для жидкой фазы
        try:
            self.S_l = self.calc_S_l(Xi_l= self.Xi_l)
            logger.log.debug('Рассчитана сумма мольных долей для жидкой фазы')

        except Exception as e:
            logger.log.error('Сумма мольных долей для жидкой фазы не рассчитана', e)


        #Нормируем мольные доли для газовой фазы
        try:
            self.yi_v =self.normalize_mole_fractions_vapour(Yi_v=self.Yi_v, S_v= self.S_v)
            logger.log.debug('Выполнена нормировка мольных долей газовой фазы')

        except Exception as e:
            logger.log.error('Нормировка мольных долей газовой фазы не выполнена', e)


        # Нормируем мольные доли для жидкой фазы
        try:
            self.xi_l =self.normalize_mole_fractions_liquid(Xi_l=self.Xi_l, S_l= self.S_l)
            logger.log.debug('Выполнена нормировка мольных долей жидкой фазы')

        except Exception as e:
            logger.log.error('Нормировка мольных долей жидкой фазы не выполнена', e)


        # Решение УРС для газовой фазы
        try:
            self.vapour_eos = self.calc_eos_for_vapour(y_i_v= self.yi_v)
            logger.log.debug('УРС для газовой фазы решено')
        except Exception as e:
            logger.log.error('УРС для газовой фазы не решено',e)


        # Решение УРС для жидкой фазы
        try:
            self.liquid_eos = self.calc_eos_for_liquid(x_i_l= self.xi_l)
            logger.log.debug('УРС для жидкой фазы решено')
        except Exception as e:
            logger.log.error('УРС для жидкой фазы не решено',e)


        # Расчет Ri_v 
        try:
            self.ri_v = self.calc_ri_vapour(self.vapour_eos)
            logger.log.info('Расчет Ri_v выполнен')
        except Exception as e:
            logger.log.error('Расчет Ri_v не выполнен', e)


        # Расчет Ri_l
        try:
            self.ri_l = self.calc_ri_liquid(self.liquid_eos)
            logger.log.info('Расчет Ri_v выполнен')
        except Exception as e:
            logger.log.error('Расчет Ri_v не выполнен', e)


        # Расчет сходимости
        try:
            self.check_convergence()

        except Exception as e:
            logger.log.error('Проверка сходимости не выполнена', e)

        

        logger.log.info('=========')
        logger.log.info('=========')

        logger.log.info('Предварительный расчет стабильности системы проведен')
        logger.log.info(f'Начальные k-values: {self.k_values}')
        logger.log.info(f'Мольные доли в газовой фазе Yi_v: {self.Yi_v}')
        logger.log.info(f'Мольные доли в жидкой фазе Xi_v: {self.Xi_l}')
        logger.log.info(f'Сумма мольных долей в газовой фазе S_v: {self.S_v}')
        logger.log.info(f'Сумма мольных долей в жидкой фазе S_l: {self.S_l}')
        logger.log.info(f'Нормированные мольные доли  в газовой фазе yi_v: {self.yi_v}')
        logger.log.info(f'Нормированные мольные доли  в жидкой фазе xi_v: {self.xi_l}')
        logger.log.info(f'Параметр ri_v в газовой фазе ri_v: {self.ri_v}')
        logger.log.info(f'Параметр ri_l в жидкой фазе ri_l: {self.ri_l}')

        logger.log.info('=========')
        logger.log.info('=========')

    ### МЕТОДЫ ###


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
        for component in list(zi.keys()):
            Yi_v[component] = zi[component] * k_values[component]

        return Yi_v


    # Расчет мольных долей в жидкой фазе
    def calc_Xi_l(self, zi: dict, k_values: dict):
        Xi_l = {}
        for component in list(zi.keys()):
            Xi_l[component] = zi[component] / k_values[component]
        
        return Xi_l


    # Расчет суммы мольных долей в газовой фазе
    def calc_S_v(self, Yi_v:dict):
        return sum(list(Yi_v.values()))
    

    # Расчет суммы мольных долей в жидкой фазе
    def calc_S_l(self, Xi_l:dict):
        return sum(list(Xi_l.values()))
    

    # Нормируем мольные доли газовой фазы
    def normalize_mole_fractions_vapour(self, Yi_v:dict, S_v: float):
        normalized_mole_fractions_vapour = {}
        for component in list(Yi_v.keys()):
            normalized_mole_fractions_vapour[component] = Yi_v[component] / S_v
        
        return normalized_mole_fractions_vapour


    # Нормируем мольные доли для жидкой фазы
    def normalize_mole_fractions_liquid(self, Xi_l:dict, S_l):
        normalized_mole_fractions_liquid = {}
        for component in list(Xi_l.keys()):
            normalized_mole_fractions_liquid[component] = Xi_l[component] / S_l
        
        return normalized_mole_fractions_liquid


    # Решаем УРС для газовой фазы
    def calc_eos_for_vapour(self, y_i_v):
        eos_for_vapour = EOS_PR(zi = y_i_v, p = self.p, t = self.t)
        
        return eos_for_vapour


    # Решаем УРС для жидкой фазы
    def calc_eos_for_liquid(self, x_i_l):
        eos_for_liquid = EOS_PR(zi= x_i_l, p = self.p, t = self.t)

        return eos_for_liquid
    


    # Рассчитываем Ri для газовой фазы
    def calc_ri_vapour(self, eos_vapour:EOS_PR):
        ri_vapour = []
        for component in eos_vapour.zi.keys():
            ri = (self.initial_eos.fugacity_by_roots[self.initial_eos.choosen_eos_root][component] /
                   (eos_vapour.fugacity_by_roots[eos_vapour.choosen_eos_root][component]) * self.S_v)
            ri_vapour.append(ri)
        
        return ri_vapour


    # Рассчитываем Ri для жидкой фазы
    def calc_ri_liquid(self, eos_liquid: EOS_PR):
        ri_liquid = []
        for component in eos_liquid.zi.keys():
            ri = (self.initial_eos.fugacity_by_roots[self.initial_eos.choosen_eos_root][component] /
                   (eos_liquid.fugacity_by_roots[eos_liquid.choosen_eos_root][component]) * self.S_l)
            ri_liquid.append(ri)
        
        return ri_liquid


    # Проверка условия стабильности 
    def check_convergence(self, e = math.pow(10, -12)):
        self.iteration = 0
        ri_v_for_sum = []
        ri_l_for_sum = []

        for ri_v in self.ri_v:
            ri_v_for_sum.append(math.pow((ri_v - 1), 2))
        ri_v_sum = sum(ri_v_for_sum)

        for ri_l in self.ri_l:
            ri_l_for_sum.append(math.pow((ri_l - 1), 2))
        ri_l_sum = sum(ri_l_for_sum)

        logger.log.info('=====')
        logger.log.info(f'Итерация: {self.iteration}')
        logger.log.info(f'Ошибка по газу: {ri_v_sum} < 1')
        logger.log.info(f'Ошибка по жидкости: {ri_l_sum} < 1')
        logger.log.info('=====')


        self.iteration += 1
        if (ri_l_sum < e) and (ri_v_sum < e):
            return True
        else:
            return False





    # Обновление констант равновесия
    def update_k_values(self):
        pass


    # Проверяем тривиальное решение 
    def check_trivial_solution(self):
        ki_v_for_sum = []
        ki_l_for_sum = []

        for ki_v in self.k_values['vapour']:
            pass

    
    # Пайплайн решения
    def stability_analysis(self):
        pass



if __name__ == '__main__':
    phs = PhaseStability(zi = {'C1':0.7, 'C2': 0.2, 'C3': 0.1}, p = 50, t = 50)
    