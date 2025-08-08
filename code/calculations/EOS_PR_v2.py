from Composition import Composition
import math as math
import cmath
import sympy as smp
import numpy as np

from logger import LogManager

logger = LogManager(__name__)

class EOS_PR:
    def __init__(self, composition:Composition, p: float, t: float):

        '''
        Класс для решения УРС Пенга-Робинсона

        Attributes:
            zi: компонентный состав смеси {'C1' : 50, 'C2': 50 ...}
            p: давление, бар
            t: температура, С

        Return:
            Z: Значение Z-фактора, определенное по приведенной энергии Гиббса
        '''
        # Читаем .yaml файл с данными по компонентам
        try:
            self.composition = composition
            self.zi = self.composition.composition
            self.db = self.composition.composition_data
            logger.log.debug('Данные компонент из Composition прочитаны успешно') 

        except Exception as e:
            logger.log.fatal('Данные компонент не найдены!', e)


        # Компонентный состав       
        if 0 in list(self.zi.values()):
            z = {k: v for k, v in self.zi.items() if v != 0}
            self.zi = z
        if sum(list(self.zi.values())) != 1:
            logger.log.fatal(f'Сумма компонентов не равна 1: {self.zi}')
            #raise ValueError
        
        else:
            logger.log.debug('Сумма компонентов равна 1')
        
        # Инициализация термобарических условий в зависимости от типа запуска модуля
        # if __name__ == '__main__':
        # # Давление для расчета
        #     self.p = p * math.pow(10,5)
        # # температура для расчета
        #     self.t = t + 273.14

        # else:
        #     self.p = p
        #     self.t = t

        # if __name__ == '__main__':
        #     self.p = p * math.pow(10,5)
        #     self.t = t + 273.14

        # else:

        if __name__ == '__main__':
            self.p = p
            self.t = t + 273.14

        else:
            self.p = p
            self.t = t

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


        # Расчет шифт-параметра
        try:
            self.shift_parametr = self.calc_shift_parametr()
        
        except Exception as e:
            logger.log.error('Шифт параметр не рассчитан')


         # Решение УРС по Кардано
        
        # Определение действительных корней УРС
        try:
            self.real_roots_eos = self.calc_cubic_eos()
            logger.log.debug(f'УРС решено, получен {len(self.real_roots_eos)} действительный корень: {self.real_roots_eos}')
            
        except Exception as e:
            logger.log.error('УРС не решено')

        # Расчет летучести для всех компонент
        try:
            self.fugacity_by_roots = {}
            for root in self.real_roots_eos:

                fugacity_by_components = {}
                for component in self.zi.keys():
                    fugacity_by_components[component] = self.calc_fugacity_for_component_PR(component, root)
                self.fugacity_by_roots[root] = fugacity_by_components
            
        except Exception as e:
            logger.log.error('Расчет летучести для компонентов не проведен', e)



        # Расчет приведенной энергии Гиббса
        try:
            self.normalized_gibbs_energy = self.calc_normalized_gibbs_energy()

        except Exception as e:
            logger.log.error('Расчет энергии Гиббса не проведен')


        # Выбор корня УРС по наименьшей энергии Гиббса
        try:
            self.choosen_eos_root = self.choose_eos_root_by_gibbs_energy()
            
            logger.log.info('==============')
            logger.log.info(f'УРС решено для смеси {self.zi}, P = {self.p} Па, T = {self.t } К')
            logger.log.info(f'Z-фактор и ln(f_i) компонент: {self.fugacity_by_roots}')
            logger.log.info(f'Z-factor и приведенные энергии Гиббса: {self.normalized_gibbs_energy}')
            logger.log.info(f'Выбранный корень по приведенной энергии Гиббса: {self.choosen_eos_root}')
            logger.log.info('==============')

        except Exception as e:
            logger.log.error('Корень по наименьшей энергии Гиббса не выбран', e)



## Методы ##


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
        return omega_a * math.pow(self.db['critical_temperature'][component],2) * math.pow(8.31, 2) * alpha / self.db['critical_pressure'][component]

    # Метод расчета параметра b для компоненты
    def calc_b(self, component, omega_b = 0.0778):
        '''
        param: component - компонент, для которого проводится расчет
        param: omega_b - константа
        '''
        return omega_b * 8.31 * self.db['critical_temperature'][component] / self.db['critical_pressure'][component]
    

    # Метод расчета параметра А для компоненты
    def calc_A(self, component):
        '''
        param: component - компонент, для которого проводится расчет
        '''
        return self.calc_a(component) * self.p/math.pow((8.31 * self.t), 2)
    
    
    # Метод расчета параметра А для компоненты
    def calc_B(self, component):
        '''
        param: component - компонент, для которого проводится расчет
        '''
        return self.calc_b(component) * self.p/ (8.31 * self.t)
    
    # Метод расчета параметра А для УРС
    def calc_mixed_A(self):
        # if len(list(self.zi.keys())) == 1 or ((len(list(self.zi.keys())) == 2) and (0 in list(self.zi.values()))):
        #     return list(self.all_params_A.values())[0]
        
        # else:
            a_mixed = []
            second_components = list(self.zi.keys())
            for i_component in self.zi.keys():
                for j_component in second_components:
                    a_mixed.append(self.zi[i_component] * self.zi[j_component] * math.sqrt(self.all_params_A[i_component] * self.all_params_A[j_component]) * (1 - self.db['bip'][i_component][j_component]))

            return sum(a_mixed)


    # Метод расчета взвешенного параметра В для УРС
    ##TODO: нужно переделать логику: использовать то, что сейчас все расчетные параметры стали храниться в словарях
    def calc_linear_mixed_B(self):
        linear_mixed_B = []
        for i, b in enumerate(list(self.all_params_B.values())):
            linear_mixed_B.append(b * list(self.zi.values())[i])
        return sum(linear_mixed_B)
        
    
    def calc_mixed_B_v2(self):
        mixed_B = []
        for i, b in enumerate(list(self.all_params_B.values())):
            mixed_B.append( b * list(self.zi.values())[i])

        return mixed_B
    
    # Метод расчета шифт-параметра
    def calc_shift_parametr(self):
        c_to_sum = []
        for component in self.zi.keys():
            c_to_sum.append(self.zi[component] * self.db['shift_parameter'][component] * self.all_params_b[component])

        return sum(c_to_sum)


    # Метод для решения кубического уравнения
    def calc_cubic_eos(self):
        bk = self.B_linear_mixed - 1
        ck = self.mixed_A - 3 * (self.B_linear_mixed ** 2) - 2 * self.B_linear_mixed
        dk = (self.B_linear_mixed ** 2) + (self.B_linear_mixed ** 3) - self.mixed_A * self.B_linear_mixed
        pk = - (bk ** 2) / 3 + ck
        qk = 2 * (bk ** 3) / 27 - (bk * ck/ 3 ) + dk
        s = ((pk/3) ** 3) + ((qk/2) ** 2) 

        if s > 0:
            vb = -qk/2 - (s ** (1/2)) #math.sqrt(s)
            itt = -qk/2 + (s ** (1/2)) #math.sqrt(s)
            if itt < 0:

                itt =  abs(itt)
                # В этой строке ломается код
                it =  (itt ** (1/3))
                it = - (itt ** (1/3))
            else:
                 it = itt ** (1/3)
            
            #it = itt ** (1/3)

            if vb < 0:
                    zk0 = it - ((abs(vb)) ** (1/3)) - bk/3
                
            else:
                    zk0 = it + ((-qk/2 - math.sqrt(s)) ** (1/3)) - bk/3

            zk1 = 0
            zk2 = 0
        
        elif s < 0:
            if qk < 0:
                f = math.atan(math.sqrt(-s) / (-qk/2))
            elif qk > 0:
                f = math.atan(math.sqrt(-s) / (-qk/2)) + math.pi
            else:
                f = math.pi / 2

            zk0 = 2 * math.sqrt(-pk/3) * math.cos(f/3) - bk/3
            zk1 = 2 * math.sqrt(-pk/3) * math.cos(f/3 + 2 * math.pi /3) - bk/3 
            zk2 = 2 * math.sqrt(-pk/3) * math.cos(f/3 + 4 * math.pi /3) - bk/3
        
        elif s == 0:
            zk0 = 2 * math.sqrt(-qk / 2) - bk/3
            zk1 = -math.pow((-qk/2), (1/3)) - bk/3
            zk2 = -math.pow((-qk/2), (1/3)) - bk/3

        #print([zk0, zk1, zk2])

        return [zk0, zk1, zk2]


    # Метод расчета летучести
    def calc_fugacity_for_component_PR(self, component, eos_root):
        '''
        Метод возвращает значение ln_f_i (формула 1.39)
        Введено доп уравнение для расчета летучести одной компоненты
        '''
        if len(list(self.zi.keys())) == 1:
            eos_roots = self.real_roots_eos
            for root in eos_roots:
                ln_fi_i = root - 1 - math.log(root - self.B_linear_mixed) - self.mixed_A / (2* math.sqrt(2) * self.B_linear_mixed) *  math.log((root + (math.sqrt(2) + 1) * self.B_linear_mixed)/(root - (math.sqrt(2) - 1) * self.B_linear_mixed))
                fi = math.exp(ln_fi_i)

                return ln_fi_i

        else:
            zi_Ai = []
            # for comp in [x for x in self.zi.keys() if x != component]:
            for comp in list(self.zi.keys()):
                zi_Ai.append(self.zi[comp] * 
                                (1 - self.db['bip'][component][comp]) * 
                                math.sqrt(self.all_params_A[component] * self.all_params_A[comp]))
            sum_zi_Ai = sum(zi_Ai)


            if (eos_root - self.B_linear_mixed) > 0:

                ln_fi_i = ((self.all_params_B[component] / self.B_linear_mixed) * (eos_root - 1) -
                            (math.log(eos_root - self.B_linear_mixed)) + 
                            (self.mixed_A / (2 * math.sqrt(2) * self.B_linear_mixed)) * 
                            ((self.all_params_B[component] / self.B_linear_mixed) - (2/self.mixed_A) *  sum_zi_Ai) * 
                            math.log((eos_root + ((1 + math.sqrt(2))* self.B_linear_mixed))/(eos_root + ((1 - math.sqrt(2))* self.B_linear_mixed))))



                ln_f_i = ln_fi_i + math.log(self.p * self.zi[component]) 



                return ln_f_i
        
            else:
                return 0

    # Метод расчета летучести для однокомпонентной смеси
    def calc_fugacity_one_component_PR(self):
        eos_roots = self.real_roots_eos
        for root in eos_roots:
            ln_fi_i = root - 1 - math.log(root - self.B_linear_mixed) - self.mixed_A / (2* math.sqrt(2) * self.B_linear_mixed) *  math.log((root + (math.sqrt(2) + 1) * self.B_linear_mixed)/(root - (math.sqrt(2) - 1) * self.B_linear_mixed))
            fi = math.exp(ln_fi_i)
            f = fi * self.p
            print(f)


    # Метод расчета летучести по Pedersen
    def calc_fugacity_for_components_pedersen(self, component, eos_root):
        if (eos_root - self.B_linear_mixed):
            # Расчет суммы j
            zj_Aj = []
            for comp in [x for x in self.zi.keys() if x != component]:
                zj_Aj.append(self.zi[comp] * 
                                (1 - self.db['bip'][component][comp]) * 
                                math.sqrt(self.all_params_A[component] * self.all_params_A[comp]))
            sum_zj_Aj = sum(zj_Aj)
            
            ln_fi_i = - (math.log(eos_root - self.B_linear_mixed) + (eos_root - 1) * (self.all_params_B[component] / self.B_linear_mixed) - 
                         (self.mixed_A / (math.pow(2, 1.5) * self.B_linear_mixed)) * 
                         ((1/self.all_params_A[component]) * 2 * math.sqrt(self.all_params_A[component])* sum_zj_Aj) - (self.all_params_B[component]/self.B_linear_mixed) * 
                         math.log((eos_root + (math.sqrt(2) + 1) * self.B_linear_mixed)/(eos_root - (math.sqrt(2) - 1) * self.B_linear_mixed)))
            
            # Расчет логарифма летучести через преобразование логарифмов
            ln_f_i = ln_fi_i + math.log(self.zi[component] * self.p)
            return ln_f_i
        
        else:
            return 0


    #Метод расчета приведенной энергии Гиббса
    def calc_normalized_gibbs_energy(self) -> dict:
        
        '''
        Метод возвращает словарь {корень УРС: значение приведенной энергии Гиббса}
        '''

        normalized_gibbs_energy = {}
        for root in self.fugacity_by_roots:
            gibbs_energy_by_roots = []
            if root == 0:
                normalized_gibbs_energy[root] = math.pow(10,6)

            else:
                for component in self.fugacity_by_roots[root].keys():
                    gibbs_energy_by_roots.append(math.exp(self.fugacity_by_roots[root][component]) * self.zi[component])
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
    comp = Composition({'C1': 0.5, 'C6': 0.4, 'C25': 0.1})

    eos = EOS_PR(comp, 5, 50)
    print(f' Z: {eos.choosen_eos_root}')
    print(f'fug_by_roots: {eos.fugacity_by_roots}')
    print(f' Е Гиббса: {eos.normalized_gibbs_energy}')







