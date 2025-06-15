import yaml
import math as math
import sympy as smp
import numpy as np

from logger import LogManager

logger = LogManager(__name__)

class EOS_PR:
    def __init__(self, zi:dict, p: float, t: float):

        '''
        param: zi - компонентный состав смеси {'C1' : 50, 'C2': 50 ...}
        param: p - давление, бар
        param: t - температура, С
        '''
        # Читаем .yaml файл с данными по компонентам
        try:
            
            with open('code/db.yaml', 'r') as db_file:
                self.db = yaml.safe_load(db_file)
            logger.log.debug('Данные компонент из .yaml прочитаны успешно') 

        except Exception as e:
            logger.log.fatal('Данные компонент не найдены!', e)


        # компонентный состав
        self.zi = zi
        if sum(list(self.zi.values())) != 100:
            logger.log.fatal('Сумма компонентов не равна 100')
            #raise ValueError
        else:
            logger.log.debug('Сумма компонентов равна 100')
        
        # z = {k: v for k, v in self.zi.items() if v >= 0.001}
        # self.zi = z

        

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
            
            logger.log.debug('Параметры a и b УРС рассчитаны для всех компонент')

        except Exception as e:
            logger.log.error('Параметры а и b УРС не рассчитаны!', e)


        # Параметры А и В, рассчитанные для всего компонентного состава
        self.all_params_A = {}
        self.all_params_B = {}

        for key in self.zi.keys():
            self.all_params_A[key] = self.calc_A(component=key)
            self.all_params_B[key] = self.calc_B(component=key)
        logger.log.debug('Параметры А и В УРС рассчитаны для всех компонент')

        # Параметр В linear mixed
        try:
            self.B_linear_mixed = self.calc_linear_mixed_B()
            logger.log.debug('Взвешенный параметр В рассчитан для УРС')
        
        except Exception as e:
            logger.log.error('Взвешенный параметр В не рассчитан')

        # Параметр А quad mixed
        try:
            self.mixed_A = self.calc_mixed_A()
            logger.log.debug('Взвешенный параметр А расчитан')
        
        except Exception as e:
            logger.log.error('Взвешенный параметр A не рассчитан')

         # Решение УРС по Кардано
        
        # Определение действительных корней УРС
        try:
            self.real_roots_eos = self.calc_cubic_eos_cardano()[0]
            logger.log.debug(f'УРС решено, получен {len(self.real_roots_eos)} действительный корень: {self.real_roots_eos}')

        except Exception as e:
            logger.log.error('УРС не решено')

        # Расчет летучести для всех компонент
        try:
            self.fugacity_by_roots = {}
            for root in self.real_roots_eos:

                fugacity_by_components = {}
                for component in self.zi.keys():
                    fugacity_by_components[component] = self.calc_fugacity_for_component_PR(component, root) #* self.zi[component] /100 * self.p
                self.fugacity_by_roots[root] = fugacity_by_components
            
            logger.log.debug('Летучести для всех компонент расчитаны')
        
        except Exception as e:
            logger.log.error('Расчет летучести для компонентов не проведен', e)

        # Расчет приведенной энергии Гиббса
        try:
            self.normalized_gibbs_energy = self.calc_normalized_gibbs_energy()
            logger.log.debug('Приведенная энергия Гиббса расчитана')

        except Exception as e:
            logger.log.error('Расчет энергии Гиббса не проведен')


        # Выбор корня УРС по наименьшей энергии Гиббса
        try:
            self.choosen_eos_root = self.choose_eos_root_by_gibbs_energy()
            logger.log.debug('Выбран корень УРС по приведенной энергии гиббса')


        except Exception as e:
            logger.log.error('Корень по наименьшей энергии Гиббса не выбран', e)

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
        if len(list(self.zi.keys())) == 1 or ((len(list(self.zi.keys())) == 2) and (0 in list(self.zi.values()))):
            return list(self.all_params_A.values())[0]
        
        else:
            a_mixed = []
            second_components = list(self.zi.keys())
            for main_component in self.zi.keys():
                for second_component in [x for x in second_components if x != main_component]:
                    a_mixed.append(self.zi[main_component]/100 * self.zi[second_component]/100 * math.sqrt(self.all_params_A[main_component] * self.all_params_A[second_component]) * (1 - self.db['bip'][main_component][second_component]))
                second_components.remove(main_component)
            return sum(a_mixed)


    # Метод расчета взвешенного параметра В для УРС
    ##TODO: нужно переделать логику: использовать то, что сейчас все расчетные параметры стали храниться в словарях
    def calc_linear_mixed_B(self):
        linear_mixed_B = []
        for i, b in enumerate(list(self.all_params_B.values())):
            linear_mixed_B.append(b * list(self.zi.values())[i]/ 100)
            return sum(linear_mixed_B)
    
    # Метод расчета УРС через numpy
    def calc_cubic_eos_numpy(self):
        coefs = [1, 
                 -(1-self.B_linear_mixed), 
                 (self.mixed_A - 3 * math.pow(self.B_linear_mixed, 2) - 2* self.B_linear_mixed), 
                 -(self.mixed_A * self.B_linear_mixed - math.pow(self.B_linear_mixed, 2) - math.pow(self.B_linear_mixed, 3))]

        roots = np.roots(coefs)
        return roots
    
    # Метод расчета УРС по Кардано
    def calc_cubic_eos_cardano(self):
        a = 1
        b = -(1-self.B_linear_mixed)
        c = (self.mixed_A - 3 * math.pow(self.B_linear_mixed, 2) - 2* self.B_linear_mixed)
        d = -(self.mixed_A * self.B_linear_mixed - math.pow(self.B_linear_mixed, 2) - math.pow(self.B_linear_mixed, 3))
        
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
        
        roots = [x1, x2, x3]

        real_roots = []
        complex_roots = []
        
        for root in roots:
            if isinstance(root, (float, int)):  # Если корень уже чисто вещественный
                real_roots.append(root)
            else:
                # Проверяем, близка ли мнимая часть к нулю (с учетом погрешности вычислений)
                if abs(root.imag) < 1e-10:  # Порог можно настроить
                    real_roots.append(root.real)
                else:
                    complex_roots.append(root)
        
        return real_roots, complex_roots
        
    
    
    # Метод расчета летучести
    ##TODO: используем Z, полученный в результате расчета УРС. Их может быть несколько, надо уточнить как быть.
    def calc_fugacity_for_component_PR(self, component, eos_root):
        zi_Ai = []
        for comp in [x for x in self.zi.keys() if x != component]:
            zi_Ai.append(self.zi[comp] / 100 * 
                             (1 - self.db['bip'][component][comp]) * 
                             math.sqrt(self.all_params_A[component] * self.all_params_A[comp]))
        sum_zi_Ai = sum(zi_Ai)

        ln_fi_i = ((self.all_params_B[component] / self.B_linear_mixed) * (eos_root - 1) -
                        (math.log(eos_root - self.B_linear_mixed)) + 
                        (self.mixed_A / (2 * math.sqrt(2) * self.B_linear_mixed)) * 
                        ((self.all_params_B[component] / self.B_linear_mixed) - (2/self.mixed_A) * sum_zi_Ai) * 
                        math.log((eos_root + ((1 + math.sqrt(2))* self.B_linear_mixed))/(eos_root - ((1 - math.sqrt(2))* self.B_linear_mixed))))


        
        return math.e ** ln_fi_i
    
    def calc_fugacity_for_component_RK(self, component, eos_root):
        zi_Ai = []
        for comp in [x for x in self.zi.keys() if x != component]:
            zi_Ai.append(self.zi[comp] / 100 * 
                             (1 - self.db['bip'][component][comp]) * 
                             math.sqrt(self.all_params_A[component] * self.all_params_A[comp]))
        sum_zi_Ai = sum(zi_Ai)
        if eos_root > 0:
            ln_fi_i = ((self.all_params_B[component] / self.B_linear_mixed) * (eos_root - 1) -
                        (math.log(eos_root - self.B_linear_mixed)) + 
                        (self.mixed_A / (self.B_linear_mixed)) * 
                        ((self.all_params_B[component] / self.B_linear_mixed) - (2/self.mixed_A) * sum_zi_Ai) * 
                        math.log(1 + (self.B_linear_mixed/eos_root)))
        
            return math.pow(math.e, ln_fi_i)
        else:
            return 0


    def calc_normalized_gibbs_energy(self):
        normalized_gibbs_energy = {}
        for root in self.fugacity_by_roots:
            gibbs_energy_by_roots = []
            for component in self.fugacity_by_roots[root].keys():
                gibbs_energy_by_roots.append(self.zi[component]/100 * math.log(self.fugacity_by_roots[root][component]))
                normalized_gibbs_energy[root] = sum(gibbs_energy_by_roots)

        return normalized_gibbs_energy 
    
    # Метод для определения корня (Z) по минимальной энергии Гиббса
    def choose_eos_root_by_gibbs_energy(self):
        '''
        return: Значение корня Z, при котором энергия Гиббса минимальна
        '''
        min_gibbs_energy = min(self.normalized_gibbs_energy.values())
        return [k for k, v in self.normalized_gibbs_energy.items() if v == min_gibbs_energy][0]
    
    

if __name__ == '__main__':
    eos = EOS_PR({'C1':100}, 5, 20)

    print(f'eos.fugacity_by_roots: {eos.fugacity_by_roots}')
    print('===')
    print(f'eos.normalized_gibbs_energy {eos.normalized_gibbs_energy}')
    print('===')
    print(f'Выбранный корень по энергии Гиббса: {eos.choose_eos_root_by_gibbs_energy()}')

