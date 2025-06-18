import logging
from logger import LogManager
from EOS_PR_v2 import EOS_PR
import math as math
import yaml
logger = LogManager(__name__)


class PhaseStability:

    def __init__(self, zi:dict, p:float, t:float):
        
        '''
        Класс для проверки стабильности системы

        Attributes:
            zi: компонентный состав смеси {'C1' : 50, 'C2': 50 ...}
            p: давление, бар
            t: температура, С

        Return:
            ##TODO:
            ...
        '''

        self.zi = zi

        # Инициализация термобарических условий в зависимости от запуска модуля
        if __name__ == '__main__':
            self.p = p * math.pow(10,5)
            self.t = t + 273
        
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

        # Инициализация начального решения УРС
        
        logger.log.debug('===')
        logger.log.debug('Запущено решение УРС для исходного состава')
        try:
            self.initial_eos_solve = EOS_PR(self.zi, self.p, self.t)
            logger.log.debug('Начальное УРС решено')
            logger.log.debug('===')
        except Exception as e:
            logger.log.error('Начальное УРС не решено')



    # Расчет начальных констант равновесия
        try:
            self.k_values = {}
            k_values_liquid = {}
            k_values_vapour = {}
            for component in list(self.zi.keys()):
                k_values_liquid[component] = (self.calc_k_initial(p_crit_i = self.db['critical_pressure'][component],
                                                                 t_crit_i = self.db['critical_temperature'][component],
                                                                 acentric_factor_i= self.db['acentric_factor'][component]))
                k_values_vapour[component] = (self.calc_k_initial(p_crit_i = self.db['critical_pressure'][component],
                                                                 t_crit_i = self.db['critical_temperature'][component],
                                                                 acentric_factor_i= self.db['acentric_factor'][component]))
            self.k_values['vapour'] = k_values_vapour
            self.k_values['liquid'] = k_values_liquid
            
            logger.log.debug('===')
            logger.log.debug(f'Значения начальных констант равновесия расчитаны: {self.k_values}')
            logger.log.debug('===')

        except Exception as e:
            logger.log.error('Начальные константы равновесия не рассчитаны', e)


        # Расчет Xi_Yi
        try:
            self.Yi_Xi = self.calc_Yi_v_and_Xi_l(zi= self.zi, k_vals= self.k_values)
            
            logger.log.debug('===')
            logger.log.debug(f'Значения Xi_Yi рассчитано: {self.Yi_and_Xi}')
            logger.log.debug('===')

        except Exception as e:
            logger.log.error('Не удалось рассчитать Yi Xi', e)


        # Расчет суммы мольных долей
        try:
            self.sum_mole_fractions = self.summerize_mole_fractions(Yi_Xi= self.Yi_Xi)
            logger.log.debug('===')
            logger.log.debug(f'Сумма мольных долей рассчитана: {self.sum_mole_fractions}')
            logger.log.debug('===')
        except Exception as e:
            logger.log.error('Расчет суммы мольных долей жидкой и газовой фазы не проведен', e)


        # Расчет нормализованных мольных долей в жидкости и в газе
        try:
            self.normalized_mole_fractions = self.normalize_mole_fraction(self.zi, self.Yi_Xi, self.sum_mole_fractions)
            
            logger.log.debug('===')
            logger.log.debug(f'Нормализованная сумма мольных долей рассчитана: {self.normalized_mole_fractions}')
            logger.log.debug('===')

        except Exception as e:
            logger.log.error('Расчет нормализованных мольных долей не проведен', e)


        ## Первая итерация
        # решение УРС для жидкой и газовой фазы
        try:
            logger.log.debug('===')
            logger.log.debug(f'Запущена первая итерация решения УРС для жидкой и газовой фазы')
            self.eos_for_liquid_first_iter = EOS_PR(self.normalized_mole_fractions['liquid'], self.p, self.t)

            self.eos_for_vapour_first_iter = EOS_PR(self.normalized_mole_fractions['vapour'], self.p, self.t)

            logger.log.debug('===')
        except Exception as e:
            logger.log.error('Не удалось инициализировать уравнения состояния', e)

        ## расчет Ri
        try:


            self.ri_vapour = self.calc_ri_vapour(self.eos_for_vapour_first_iter)
            logger.log.debug('===')
            logger.log.debug(f'Рассчитано Ri_vapour: {self.ri_vapour}')
            logger.log.debug('===')

            self.ri_liquid = self.calc_ri_liquid(self.eos_for_liquid_first_iter)
            logger.log.debug('===')
            logger.log.debug(f'Рассчитано Ri_liquid: {self.ri_liquid}')
            logger.log.debug('===')

        except Exception as e:
            logger.log.error('Не рассчитаны Ri жидкой и газовой фазы для  первой итерации', e)

        # Расчет cходимости
        #self.convergence = self.check_convergence()


        # Процесс анализа стабильности системы
        try:
            self.stability_analysis()

        except Exception as e:
            logger.log.error('Не удалось провести анализ стабильности', e)


## Методы ##

    # Метод для расчета начальных констант равновесия 
    def calc_k_initial(self, p_crit_i, t_crit_i, acentric_factor_i):
        return math.pow(math.e, (5.37*(1+acentric_factor_i)*(1-(t_crit_i/self.t)))) / (self.p/p_crit_i)
    
    # Метод для расчета Yi_v и Xi_l
    def calc_Yi_v_and_Xi_l(self, zi:dict, k_vals):
        Yi_and_Xi = {}
        vapour = {}
        liquid = {}
        for component in list(zi.keys()):
            vapour[component] = self.zi[component] / 100 * k_vals['vapour'][component]
            liquid[component] = self.zi[component] / (100 * k_vals['liquid'][component])
        Yi_and_Xi['vapour'] = vapour
        Yi_and_Xi['liquid'] = liquid
        self.Yi_and_Xi = Yi_and_Xi
        return Yi_and_Xi

    # метод расчета суммы мольных долей
    def summerize_mole_fractions(self, Yi_Xi):
        sum_mole_fractions = {'vapour': sum(list(Yi_Xi['vapour'].values())),
                              'liquid': sum(list(Yi_Xi['liquid'].values()))}
        self.sum_mole_fractions = sum_mole_fractions
        return sum_mole_fractions

    # Метод для нормализации мольных долей
    def normalize_mole_fraction(self, zi, Yi_Xi, sum_mole_fractions):
        normalized_mole_fractions = {}
        normalized_vapour_fractions = {}
        normalized_liquid_fractions = {}
        for component in list(zi.keys()):
            normalized_vapour_fractions[component] = round(Yi_Xi['vapour'][component] / sum_mole_fractions['vapour'] * 100, 5)

        for component in list(zi.keys()):
            normalized_liquid_fractions[component] = round(Yi_Xi['liquid'][component] / sum_mole_fractions['liquid'] * 100, 5)

        normalized_mole_fractions['vapour'] = normalized_vapour_fractions
        normalized_mole_fractions['liquid'] = normalized_liquid_fractions
        self.normalized_mole_fractions = normalized_mole_fractions
        return normalized_mole_fractions


    # метод  расчета Ri для газовой фазы
    def calc_ri_vapour(self, eos):
        ri_vapour = {}
        for component in eos.fugacity_by_roots[eos.choosen_eos_root]:
            ri_vapour[component] = (self.initial_eos_solve.fugacity_by_roots[self.initial_eos_solve.choosen_eos_root][component] / 
                        (eos.fugacity_by_roots[eos.choosen_eos_root][component]) * self.sum_mole_fractions['vapour'])
        self.ri_vapour = ri_vapour
        return ri_vapour
    
    # Метод  расчета Ri для жидкой фазы
    def calc_ri_liquid(self, eos):
        ri_liquid = {}
        for component in eos.fugacity_by_roots[eos.choosen_eos_root]:

            ri_liquid[component] = (eos.fugacity_by_roots[eos.choosen_eos_root][component] * self.sum_mole_fractions['liquid'] / 
                                    self.initial_eos_solve.fugacity_by_roots[self.initial_eos_solve.choosen_eos_root][component])

        self.ri_liquid = ri_liquid
        return ri_liquid

    # Метод  расчета сходимости
    def check_convergence(self, epsilon = math.pow(10, -12)):
        ri_vapour_for_convergence = []
        ri_liquid_for_convergence = []
        for i in self.ri_vapour.values():
            ri_vapour_for_convergence.append(math.pow((i-1),2))
        for i in self.ri_liquid.values():
            ri_liquid_for_convergence.append(math.pow((i-1),2))

        if (sum(ri_vapour_for_convergence) < epsilon) and (sum(ri_liquid_for_convergence) < epsilon):
            return True
        else:
            return False

    def check_trivial_solution(self):
        sum_ki_vapour = []
        sum_ki_liquid = []

        for component in self.k_values['vapour']:
            sum_ki_vapour.append(math.pow((math.log(self.k_values['vapour'][component])),2))

        for component in self.k_values['liquid']:
            sum_ki_liquid.append(math.pow((math.log(self.k_values['liquid'][component])), 2))

        
        if ((sum(sum_ki_vapour)) < math.pow(10, -4)) and ((sum(sum_ki_liquid)) < math.pow(10, -4)):
            logger.log.info('Оба условия тривиального решения выполнены')
            return True
        
        elif ((sum(sum_ki_vapour)) < math.pow(10, -4)):
            logger.log.info('Выполнено условие тривиального решения для газовой фазы')
            return True
        
        elif ((sum(sum_ki_liquid)) < math.pow(10, -4)):
            logger.log.info('Выполнено условие тривиального решения для жидкой фазы')
            return True
        
        else:
            logger.log.warning('Тривиальное решение не получено')
            return False
        

    # Метод расчета новых Ki
    def update_ki(self):
        new_k_values = {}
        k_vals_liquid = {}
        k_vals_vapour = {}
        for component in self.k_values['vapour']:
            k_vals_vapour[component] = self.ri_vapour[component] * self.k_values['vapour'][component]

        
        for component in self.k_values['liquid']:
            k_vals_liquid[component] = self.ri_liquid[component] * self.k_values['liquid'][component]



        new_k_values['vapour'] = k_vals_vapour
        new_k_values['liquid'] = k_vals_liquid

        self.k_values = new_k_values

    
    def define_state_of_mixture(self):
        ...

    def stability_analysis(self):
        iter = 0
        while self.check_convergence() == False:
            iter += 1
            print('===')
            print(iter)
            print('===')
            self.update_ki()
            self.calc_Yi_v_and_Xi_l(self.zi, self.k_values)
            self.summerize_mole_fractions(self.Yi_and_Xi)
            #print(f'sum mole fractions {self.sum_mole_fractions} on iter {iter}')
            self.normalize_mole_fraction(self.zi, self.Yi_and_Xi, self.sum_mole_fractions)

            print(f'liquid_comp: {self.normalized_mole_fractions['liquid']}')
            print(f'vapour_comp: {self.normalized_mole_fractions['vapour']}')


            eos_liquid = EOS_PR(self.normalized_mole_fractions['liquid'], self.p, self.t)
            
            eos_vapour = EOS_PR(self.normalized_mole_fractions['vapour'], self.p, self.t)



            self.calc_ri_liquid(eos= eos_liquid)
            self.calc_ri_vapour(eos = eos_vapour)
            self.check_convergence()


            if self.check_trivial_solution():
                break
            else:
                continue

    



    


if __name__ == '__main__':

    phase_stability = PhaseStability({'C1': 90, 'C3': 10}, p = 50, t = 50)







