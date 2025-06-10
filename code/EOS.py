import yaml
import math as math
from Logger import LogManager

logger = LogManager(__name__)

class EOS_PR:
    def __init__(self, zi:dict, p: float, t: float):

        '''
        param: zi - компонентный состав смеси {'C1' : 50, 'C2': 50}
        param: p - давление, бар
        param: t - температура, С
        '''

        try:
            # Читаем .yaml файл с данными по компонентам
            with open('code/db.yaml', 'r') as db_file:
                self.db = yaml.safe_load(db_file)
            logger.log.info('Данные компонент из .yaml прочитаны успешно') 

        except Exception as e:
            logger.log.fatal('Данные компонент не найдены!', e)


        # компонентный состав
        self.zi = zi
        if sum(list(self.zi.values())) != 100:
            logger.log.fatal('Сумма компонентов не равна 100')
            raise ValueError
        else:
            logger.log.info('Сумма компонентов равна 100')


        if len(self.zi.keys()) > 1:
            logger.log.info('Число компонент больше 1')
        else:
            logger.log.info('Для расчета передана однокомпонентная смесь')


        # Давление для расчета
        self.p = p * math.pow(10,5)

        # температура для расчета
        self.t = t + 273

        # параметры а и b, рассчитанные для всего заданного компонентного состава
        try:
            self.all_params_a = []
            self.all_params_b = []
            for key in self.zi.keys():
                self.all_params_a.append(self.calc_a(component=key))
                self.all_params_b.append(self.calc_b(component=key))
            
            logger.log.info('Параметры a и b УРС рассчитаны для всех компонент')

        except Exception as e:
            logger.log.error('Параметры а и b УРС не рассчитаны!')


        # Параметры А и В, рассчитанные для всего компонентного состава
        self.all_params_A = []
        self.all_params_B = []

        for key in self.zi.keys():
            self.all_params_A.append(self.calc_A(component=key))
            self.all_params_B.append(self.calc_B(component=key))
        logger.log.info('Параметры А и В УРС рассчитаны для всех компонент')

        # Параметр В linear mixed
        try:
            self.B_linear_mixed = self.calc_linear_mixed_B()
            logger.log.info('Взвешенный параметр В рассчитан для УРС')
        
        except Exception as e:
            logger.log.error('Взвешенный параметр В не рассчитан')



    # Метод  расчета параметра а для компоненты
    def calc_a(self, component, omega_a = 0.45724):
        '''
        param: component - компонент, для которого проводится расчет
        param: omega_a - константа
        '''
        if self.db['acentric_factor'][component] > 0.49:
            m = 0.3796 + 1.485 * self.db['acentric_factor'][component]  - 0.1644 * math.pow(self.db['acentric_factor'][component],2) + 0.01667 * math.pow(self.db['acentric_factor'][component], 3)
        else:
            m = 0.37464 + 1.54226 * self.db['acentric_factor'][component] - 0.26992 * math.pow(self.db['acentric_factor'][component], 2)

        alpha = math.pow(1 + m * (1 - math.sqrt(self.t/self.db['critical_temperature'][component])), 2)
        return omega_a * math.pow(self.db['critical_temperature'][component],2) * math.pow(8.314,2) * alpha / self.db['critical_pressure'][component]

    # Метод расчета параметра b для компоненты
    def calc_b(self, component, omega_b = 0.0778):
        '''
        param: component - компонент, для которого проводится расчет
        param: omega_b - константа
        '''
        return omega_b * 8.314 * self.db['critical_temperature'][component] / self.db['critical_pressure'][component]
    

    # Метод расчета параметра А для компоненты
    def calc_A(self, component):
        '''
        param: component - компонент, для которого проводится расчет
        '''
        return self.calc_a(component) * self.p/math.pow((8.314 * self.t), 2)
    
    
    # Метод расчета параметра А для компоненты
    def calc_B(self, component):
        '''
        param: component - компонент, для которого проводится расчет
        '''
        return self.calc_b(component) * self.p/ (8.314 * self.t)
    
    def calc_linear_mixed_B(self):
        linear_mixed_B = []
        for i, b in enumerate(self.all_params_B):
            linear_mixed_B.append(b * list(self.zi.values())[i])
            return sum(linear_mixed_B)



if __name__ == '__main__':
    eos = EOS_PR({'C1': 50, 'C2': 50}, 100, 100)
    print(eos.all_params_a)
    print(eos.all_params_b)
    print(eos.all_params_A)
    print(eos.all_params_B)
    print(eos.B_linear_mixed)