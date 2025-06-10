import yaml
import math as math
import sympy as smp
import numpy as np
from Logger import LogManager

logger = LogManager(__name__)

class EOS_PR:
    def __init__(self, zi:dict, p: float, t: float):

        '''
        param: zi - компонентный состав смеси {'C1' : 50, 'C2': 50 ...}
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
        self.t = t + 273.14

        # параметры а и b, рассчитанные для всего заданного компонентного состава
        try:
            self.all_params_a = {}
            self.all_params_b = {}
            for key in self.zi.keys():
                self.all_params_a[key] = self.calc_a(component=key)
                self.all_params_b[key] = self.calc_b(component=key)
            
            logger.log.info('Параметры a и b УРС рассчитаны для всех компонент')

        except Exception as e:
            logger.log.error('Параметры а и b УРС не рассчитаны!')


        # Параметры А и В, рассчитанные для всего компонентного состава
        self.all_params_A = {}
        self.all_params_B = {}

        for key in self.zi.keys():
            self.all_params_A[key] = self.calc_A(component=key)
            self.all_params_B[key] = self.calc_B(component=key)
        logger.log.info('Параметры А и В УРС рассчитаны для всех компонент')

        # Параметр В linear mixed

        try:
            self.B_linear_mixed = self.calc_linear_mixed_B()
            logger.log.info('Взвешенный параметр В рассчитан для УРС')
        
        except Exception as e:
            logger.log.error('Взвешенный параметр В не рассчитан')

        # Параметр А quad mixed
        try:
            self.mixed_A = self.calc_mixed_A()

        except Exception as e:
            logger.log.error('Mixed A не рассчитан')


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
    
    # Метод расчета параметра А для УРС
    def calc_mixed_A(self):
        if len(list(self.zi.keys())) == 1:
            return list(self.all_params_A.values())[0]
        
        else:
            a_mixed = []
            for main_component in self.zi.keys():
                for second_component in [x for x in self.zi.keys() if x != main_component]:
                    a_mixed.append(self.zi[main_component]/100 * self.zi[second_component]/100 * math.sqrt(self.all_params_A[main_component] * self.all_params_A[second_component]) * (1 - self.db['bip'][main_component][second_component]))
            return sum(a_mixed)


    # Метод расчета взвешенного параметра В для УРС
    ##TODO: нужно переделать логику: использовать то, что сейчас все расчетные параметры стали храниться в словарях
    def calc_linear_mixed_B(self):
        linear_mixed_B = []
        for i, b in enumerate(list(self.all_params_B.values())):
            linear_mixed_B.append(b * list(self.zi.values())[i]/ 100)
            return sum(linear_mixed_B)

    ##TODO: НЕ РАБОТАЕТ
    def calc_cubic_eos_sympy(self):
        z = smp.symbols('z')
        equation = smp.Eq(math.pow(z, 3) - (1-self.B_linear_mixed) * math.pow(z,2) + (self.mixed_A - 3 * math.pow(self.B_linear_mixed, 2) - 2* self.B_linear_mixed) - (self.mixed_A * self.B_linear_mixed - math.pow(self.B_linear_mixed, 2) - math.pow(self.B_linear_mixed, 3)), 0)
        solution = smp.solve(equation, z)
        return solution
    

    def calc_cubic_eos_numpy(self):
        coefs = [1, 
                 (1-self.B_linear_mixed), 
                 (self.mixed_A - 3 * math.pow(self.B_linear_mixed, 2) - 2* self.B_linear_mixed), 
                 (self.mixed_A * self.B_linear_mixed - math.pow(self.B_linear_mixed, 2) - math.pow(self.B_linear_mixed, 3))]

        roots = np.roots(coefs)
        return roots
    

    def calc_cubic_eos_cardano(self):
        a = 1
        b = 1-self.B_linear_mixed
        c = (self.mixed_A - 3 * math.pow(self.B_linear_mixed, 2) - 2* self.B_linear_mixed)
        d = (self.mixed_A * self.B_linear_mixed - math.pow(self.B_linear_mixed, 2) - math.pow(self.B_linear_mixed, 3))
        # Приводим уравнение к виду x³ + px² + qx + r = 0
        p = b / a
        q = c / a
        r = d / a
        
        # Депрессированное кубическое уравнение: y³ + my + n = 0
        m = (3*q - p**2) / 3
        n = (2*p**3 - 9*p*q + 27*r) / 27
        
        # Дискриминант
        delta = (n**2)/4 + (m**3)/27
        
        if delta > 0:
            # Один действительный корень
            u = (-n/2 + math.sqrt(delta))**(1/3)
            v = (-n/2 - math.sqrt(delta))**(1/3)
            y1 = u + v
            y2 = -(u+v)/2 + (u-v)*math.sqrt(3)/2j
            y3 = -(u+v)/2 - (u-v)*math.sqrt(3)/2j
        elif delta == 0:
            # Три действительных корня (один кратный)
            if n == 0:
                y1 = y2 = y3 = 0
            else:
                u = (-n/2)**(1/3)
                y1 = 2*u
                y2 = y3 = -u
        else:
            # Тригонометрическая форма (три действительных корня)
            theta = math.acos(3*n/(2*m*math.sqrt(-m/3)))
            y1 = 2 * math.sqrt(-m/3) * math.cos(theta/3)
            y2 = 2 * math.sqrt(-m/3) * math.cos((theta + 2*math.pi)/3)
            y3 = 2 * math.sqrt(-m/3) * math.cos((theta + 4*math.pi)/3)
        
        # Возвращаемся к исходной переменной x = y - p/3
        p3 = p/3
        x1 = y1 - p3
        x2 = y2 - p3
        x3 = y3 - p3
    
        return [x1, x2, x3]



if __name__ == '__main__':
    eos = EOS_PR({'C1': 100}, 100, 100)
    print(eos.all_params_a)
    print(eos.all_params_b)
    print(eos.all_params_A)
    print(eos.all_params_B)
    print(eos.B_linear_mixed)
    print(eos.calc_mixed_A())
    print(eos.calc_cubic_eos_numpy())
    print(eos.calc_cubic_eos_cardano())