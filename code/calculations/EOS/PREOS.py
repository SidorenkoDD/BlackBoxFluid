from pathlib import Path
import sys
# Добавляем корневую директорию в PYTHONPATH
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))


from calculations.EOS.BaseEOS import EOS
import math as math




from calculations.Composition.Composition import Composition

class PREOS(EOS):
    def __init__(self, zi, components_properties, p, t):
        super().__init__(zi, components_properties, p, t)
    
        self.zi = zi
        self.components_properties = components_properties
        self.p = p
        self.t = t

    
    # Метод  расчета параметра а для компоненты
    def calc_a(self, component, omega_a = 0.45724):
        '''
        param: component - компонент, для которого проводится расчет
        param: omega_a - константа
        '''
        if self.components_properties['acentric_factor'][component] > 0.49:
            m = 0.3796 + 1.485 * self.components_properties['acentric_factor'][component]  - 0.1644 * math.pow(self.components_properties['acentric_factor'][component],2) + 0.01667 * math.pow(self.components_properties['acentric_factor'][component], 3)
        else:
            m = 0.37464 + 1.54226 * self.components_properties['acentric_factor'][component] - 0.26992 * math.pow(self.components_properties['acentric_factor'][component], 2)

        alpha = math.pow(1 + m * (1 - math.sqrt(self.t/self.components_properties['critical_temperature'][component])), 2)
        return omega_a * math.pow(self.components_properties['critical_temperature'][component],2) * math.pow(8.31, 2) * alpha / self.components_properties['critical_pressure'][component]

    # Метод расчета параметра b для компоненты
    def calc_b(self, component, omega_b = 0.0778):
        '''
        param: component - компонент, для которого проводится расчет
        param: omega_b - константа
        '''
        return omega_b * 8.31 * self.components_properties['critical_temperature'][component] / self.components_properties['critical_pressure'][component]
    

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
                    a_mixed.append(self.zi[i_component] * self.zi[j_component] * math.sqrt(self.all_params_A[i_component] * self.all_params_A[j_component]) * (1 - self.components_properties['bip'][i_component][j_component]))

            return sum(a_mixed)


    # Метод расчета взвешенного параметра В для УРС
    def calc_linear_mixed_B(self):
        linear_mixed_B = []
        for i, b in enumerate(list(self.all_params_B.values())):
            linear_mixed_B.append(b * list(self.zi.values())[i])
        return sum(linear_mixed_B)
        
    
    
    # Метод расчета шифт-параметра
    def calc_shift_parametr(self):
        c_to_sum = []
        for component in self.zi.keys():
            c_to_sum.append(self.zi[component] * self.components_properties['shift_parameter'][component] * self.all_params_b[component])

        return sum(c_to_sum)


    # Метод для решения кубического уравнения
    def solve_cubic_equation(self):
        bk = self.B_linear_mixed - 1
        ck = self.mixed_A - 3 * (self.B_linear_mixed ** 2) - 2 * self.B_linear_mixed
        dk = (self.B_linear_mixed ** 2) + (self.B_linear_mixed ** 3) - self.mixed_A * self.B_linear_mixed
        # тут было pk = -(bk ** 2) / 3 + ck
        pk = pk = -(bk ** 2) / 3 + ck
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


    # Метод расчета летучести (используемый)
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
                                (1 - self.components_properties['bip'][component][comp]) * 
                                math.sqrt(self.all_params_A[component] * self.all_params_A[comp]))
            sum_zi_Ai = sum(zi_Ai)


            if ((eos_root - self.B_linear_mixed) > 0) and (eos_root > 0):

                ln_fi_i = ((self.all_params_B[component] / self.B_linear_mixed) * (eos_root - 1) -
                            (math.log(eos_root - self.B_linear_mixed)) + 
                            (self.mixed_A / (2 * math.sqrt(2) * self.B_linear_mixed)) * 
                            ((self.all_params_B[component] / self.B_linear_mixed) - (2/self.mixed_A) *  sum_zi_Ai) * 
                            math.log((eos_root + ((1 + math.sqrt(2))* self.B_linear_mixed))/(eos_root + ((1 - math.sqrt(2))* self.B_linear_mixed))))


                #try:
                #print(component, self.zi[component])
                ln_f_i = ln_fi_i + math.log(self.p * self.zi[component]) 
                    #return ln_f_i
                #except ValueError as e:
                #    if "math domain error" in str(e):
                #        return 0 





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
            


    #Метод расчета приведенной энергии Гиббса
    def calc_normalized_gibbs_energy(self) -> dict:
        
        '''
        Метод возвращает словарь {корень УРС: значение приведенной энергии Гиббса}
        '''

        normalized_gibbs_energy = {}
        for root in self.fugacity_by_roots:
            gibbs_energy_by_roots = []
            if root <= 0:
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
    

    def calc_eos(self):
        self.all_params_a = {}
        self.all_params_b = {}
        for key in self.zi.keys():
            self.all_params_a[key] = self.calc_a(component=key)
            self.all_params_b[key] = self.calc_b(component=key)

        self.all_params_A = {}
        self.all_params_B = {}

        for key in self.zi.keys():
            self.all_params_A[key] = self.calc_A(component=key)
            self.all_params_B[key] = self.calc_B(component=key)

        self.mixed_A = self.calc_mixed_A()
        self.B_linear_mixed = self.calc_linear_mixed_B()
        self.shift_parametr = self.calc_shift_parametr()

        self.real_roots_eos = self.solve_cubic_equation()

        self.fugacity_by_roots = {}
        for root in self.real_roots_eos:
            fugacity_by_components = {}
            for component in self.zi.keys():
                fugacity_by_components[component] = self.calc_fugacity_for_component_PR(component, root)
            self.fugacity_by_roots[root] = fugacity_by_components

        self.normalized_gibbs_energy = self.calc_normalized_gibbs_energy()
        self.choosen_eos_root = self.choose_eos_root_by_gibbs_energy()
        self.choosen_fugacities = self.fugacity_by_roots[self.choosen_eos_root]

        self._fugacities = self.choosen_fugacities
        self._z = self.choosen_eos_root
        return self.choosen_eos_root, self.choosen_fugacities
    
    # def return_eos_root_and_fugacities(self):
    #     return super().return_eos_root_and_fugacities()
    
    @property
    def z(self):
        return super().z()


    @property
    def fugacities(self):
        return super().fugacities()

    


if __name__ == '__main__':
    comp = Composition({'C1': 0.5, 'C2':0.5},
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'kesler_lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'Edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'})

    eos = PREOS(comp.composition,comp.composition_data, 0.1, 293)
    eos.calc_eos()
    print(f' Z: {eos.z}')
    print(f'fug_by_roots: {eos.fugacities}')
    print(f' Е Гиббса: {eos.normalized_gibbs_energy}')