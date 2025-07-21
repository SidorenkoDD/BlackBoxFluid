import yaml
import math
from logger import LogManager
from EOS_PR_v2 import EOS_PR

logger = LogManager(__name__)


class PhaseStability:

    def __init__(self, zi: dict, p: float, t: float):
        
        # инициализируем состав
        self.zi = zi
        
        # # инициализируем термобарику
        if __name__ == '__main__':
            self.p = p
            self.t = t + 273.14
        
        else:
            self.p = p
            self.t = t


        self.convergence = False
        self.convergence_trivial_solution = False


        # Подключение к yaml-файлику
        try:
            with open('code/calculations/db.yaml', 'r') as db_file:
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

        ## Для газа
        try:
            self.k_values_vapour = self.calc_k_initial_for_vapour_wilson()
            logger.log.debug('Начальные константы равновесия для газовой фазы рассчитаны')
            
        except Exception as e:
            logger.log.error('Начальные константы равновесия для газовой фазы не рассчитаны', e)

        ## Для жидкости
        try:
            self.k_values_liquid = self.calc_k_initial_for_liquid_wilson()
            logger.log.debug('Начальные константы равновесия для жидкой фазы рассчитаны')
            
        except Exception as e:
            logger.log.error('Начальные константы равновесия для жидкой фазы не рассчитаны', e)


        # Расчет мольных долей в газовой фазе
        try:
            self.Yi_v = self.calc_Yi_v(zi = self.zi)
            logger.log.debug('мольные доли для газовой фазы рассичтаны')

        except Exception as e:
            logger.log.error('мольные доли для газовой фазы не рассчитаны', e)

        
        # Расчет мольных долей в жидкой фазе
        try:
            self.Xi_l = self.calc_Xi_l(zi = self.zi)
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
            logger.log.info('Расчет Ri_l выполнен')
        except Exception as e:
            logger.log.error('Расчет Ri_l не выполнен', e)


        try:
            self.stability_loop()
            self.interpetate_stability_analysis()

        except Exception as e:
            ...
        logger.log.info('=========')
        logger.log.info('=========')

        logger.log.info('Предварительный расчет стабильности системы проведен')
        logger.log.info(f'Начальные k-values для газовой фазы: {self.k_values_vapour}')
        logger.log.info(f'Начальные k-values для жидкой фазы: {self.k_values_liquid}')
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
            k_initial[component] = (math.pow(math.e, 5.37 * (1 + self.db['acentric_factor'][component]) * 
                                             (1 - (self.db['critical_temperature'][component]/self.t))) / 
                                    (self.p / self.db['critical_pressure'][component]))
            
        return k_initial
    

    # Расчет начальных констант равновесия для газовой фазы
    def calc_k_initial_for_vapour_wilson(self):
        k_initial_vapour = {}
        for component in list(self.zi.keys()):
            k_initial_vapour[component] = (math.pow(math.e, 5.37 * (1 + self.db['acentric_factor'][component]) 
                                                    * (1 - (self.db['critical_temperature'][component]/self.t))) / 
                                    (self.p / self.db['critical_pressure'][component]))
            
        return k_initial_vapour
    

    # Расчет начальных констант равновесия для газовой фазы
    def calc_k_initial_for_liquid_wilson(self):
        k_initial_liquid = {}
        for component in list(self.zi.keys()):
            # k_initial_liquid[component] = (math.pow(math.e, 5.37 * (1 + self.db['acentric_factor'][component]) 
            #                                         * (1 - (self.db['critical_temperature'][component]/self.t))) / 
            #                         (self.p / self.db['critical_pressure'][component]))
            k_initial_liquid[component] = math.exp(5.37 * (1 + self.db['acentric_factor'][component]) * (1 - (self.db['critical_temperature'][component]/self.t))) / (self.p / self.db['critical_pressure'][component])
            
        return k_initial_liquid
    

    # Расчет мольных долей в газовой фазе
    def calc_Yi_v(self, zi: dict):
        Yi_v = {}
        for component in list(self.k_values_vapour.keys()):
            Yi_v[component] = zi[component] * self.k_values_vapour[component]  
        return Yi_v


    # Расчет мольных долей в жидкой фазе
    def calc_Xi_l(self, zi: dict):
        Xi_l = {}
        for component in list(self.k_values_liquid.keys()):
            Xi_l[component] = zi[component] / self.k_values_liquid[component]    
        
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
            normalized_mole_fractions_vapour[component] = Yi_v[component] / S_v #round((Yi_v[component] / S_v), 5)
            #normalized_mole_fractions_vapour[component] = round((Yi_v[component] / S_v), 5)
        return normalized_mole_fractions_vapour


    # Нормируем мольные доли для жидкой фазы
    def normalize_mole_fractions_liquid(self, Xi_l:dict, S_l:float):
        normalized_mole_fractions_liquid = {}
        for component in list(Xi_l.keys()):
            normalized_mole_fractions_liquid[component] = Xi_l[component] / S_l #round((Xi_l[component] / S_l), 5)
            #normalized_mole_fractions_liquid[component] = round((Xi_l[component] / S_l), 5)
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
        ri_vapour = {}
        for component in eos_vapour.zi.keys():
            ri = ((math.e ** self.initial_eos.fugacity_by_roots[self.initial_eos.choosen_eos_root][component]) /
                   (((math.e ** eos_vapour.fugacity_by_roots[eos_vapour.choosen_eos_root][component])) * self.S_v))
            ri_vapour[component] = ri
        return ri_vapour


    # Рассчитываем Ri для жидкой фазы
    def calc_ri_liquid(self, eos_liquid: EOS_PR):
        ri_liquid = {}
        for component in eos_liquid.zi.keys():
            ri = (((math.e ** eos_liquid.fugacity_by_roots[eos_liquid.choosen_eos_root][component]))/
                  (math.e ** self.initial_eos.fugacity_by_roots[self.initial_eos.choosen_eos_root][component]) * self.S_l)
            ri_liquid[component] = ri 
        return ri_liquid


    # Обновление констант равновесия
    ## Для газовой фазы
    def update_k_values_vapour(self):
        new_k_i_vapour = {}
        for component in self.ri_v.keys():
            new_k_i_vapour[component] = self.k_values_vapour[component] * self.ri_v[component]
        

        return new_k_i_vapour


    ## Для жидкой фазы
    def update_k_values_liquid(self):
        new_k_i_liquid = {}
        for component in self.ri_l.keys():
            new_k_i_liquid[component] = self.k_values_liquid[component] * self.ri_l[component]
        

        return new_k_i_liquid
    

    ### Новый метод анализа стабильности 
    def check_convergence(self, e = math.pow(10, -5)):
    

        ri_v_to_sum = []
        ri_l_to_sum = []

        for ri_v in list(self.ri_v.values()):
            ri_v_to_sum.append((ri_v-1) ** 2)

        for ri_l in list(self.ri_l.values()):
            ri_l_to_sum.append((ri_l-1) ** 2)

        sum_ri_v = sum(ri_v_to_sum)
        sum_ri_l = sum(ri_l_to_sum)

        

        if (sum_ri_v < e) or (sum_ri_l < e):
            self.convergence = True
            return True
        
        else:
            self.convergence = False
            return False
        

    def check_trivial_solution(self):
        self.trivial_solution_vapour = False
        self.trivial_solution_liquid = False

        ki_v_to_sum = []
        for ki_v in list(self.k_values_vapour.values()):
            ki_v_to_sum.append(math.pow((math.log(ki_v)),2))
        
        ki_l_to_sum = []
        for ki_l in list(self.k_values_liquid.values()):
            ki_l_to_sum.append(math.pow((math.log(ki_l)),2))

        if sum(ki_v_to_sum) < math.pow(10,-4):
            self.trivial_solution_vapour = True
            #self.convergence_trivial_solution = True


        elif sum(ki_l_to_sum) < math.pow(10,-4):
            self.trivial_solution_liquid = True
            #self.convergence_trivial_solution = True

        if self.trivial_solution_liquid and self.trivial_solution_vapour:
            self.convergence_trivial_solution = True
        else:
            self.convergence_trivial_solution = False
        #else:
            #self.convergence_trivial_solution = False
        

    def stability_loop(self):
        iter = 0
        self.check_convergence()
        self.check_trivial_solution()
        while (self.convergence == False) and (self.convergence_trivial_solution == False):

            # self.k_values_vapour = self.update_k_values_vapour()
            # self.k_values_liquid = self.update_k_values_liquid()
    
            self.Yi_v = self.calc_Yi_v(self.zi)
            self.Xi_l = self.calc_Xi_l(self.zi)

            self.S_v = self.calc_S_v(Yi_v=self.Yi_v)
            self.S_l = self.calc_S_l (Xi_l= self.Xi_l)

            self.yi_v = self.normalize_mole_fractions_vapour(self.Yi_v, self.S_v)
            self.xi_l = self.normalize_mole_fractions_liquid(self.Xi_l, self.S_l)

            self.vapour_eos = self.calc_eos_for_vapour(self.yi_v)
            self.liquid_eos = self.calc_eos_for_vapour(self.xi_l)


            self.ri_v = self.calc_ri_vapour(self.vapour_eos)
            self.ri_l = self.calc_ri_liquid(self.liquid_eos)
            
            self.k_values_vapour = self.update_k_values_vapour()
            self.k_values_liquid = self.update_k_values_liquid()

            iter += 1
            self.check_convergence()
            self.check_trivial_solution()



            if iter > 100000:
                break


    def interpetate_stability_analysis(self):
        print(self.S_v, self.S_l)
        print(self.trivial_solution_vapour, self.trivial_solution_liquid)

        if ((self.trivial_solution_vapour) or 
            ((self.S_v <= 1) and (self.trivial_solution_liquid)) or 
            ((self.trivial_solution_vapour) and (self.S_l <= 1)) or 
            ((self.S_v <= 1) and (self.S_l<= 1))):

            # logger.log.info('===============')
            # logger.log.info('Результат интерпритации анализа стабильности:')
            # logger.log.info(f'S_v: {self.S_v}, S_l: {self.S_l}')
            # logger.log.info('Система стабильна')
            self.stable = True
            # logger.log.info('===============')


        elif (((self.S_v > 1) and self.trivial_solution_liquid) or 
              ((self.trivial_solution_vapour) and (self.S_l> 1)) or 
                ((self.S_v > 1) and (self.S_l > 1)) or 
                ((self.S_v> 1) and (self.S_l <= 1)) or 
                ((self.S_v <= 1) and (self.S_l > 1))):
            
            # logger.log.info('===============')
            # logger.log.info('Результат интерпритации анализа стабильности:')
            # logger.log.info(f'S_v: {self.S_v}, S_l: {self.S_l}')
            # logger.log.info('Система не стабильна')
            self.stable = False
            # logger.log.info('===============')



if __name__ == '__main__':
    phs = PhaseStability({'C1':0.6 , 'C6': 0.4}, 14.45, 0)

    #phs.stability_loop()
    print(phs.convergence_trivial_solution)
    print(phs.S_v)
    print(phs.S_l)
    
    #phs.interpetate_stability_analysis()

    print(phs.k_values_vapour)
    print(phs.k_values_liquid)
    print(phs.xi_l)
    print(phs.yi_v)
    print(phs.stable)
    print(phs.initial_eos.fugacity_by_roots)
    print(phs.vapour_eos.fugacity_by_roots)


