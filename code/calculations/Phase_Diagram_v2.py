from Composition import Composition
from PhaseStability_v3 import PhaseStability
import math as math
import numpy as np


class PhaseDiagram:

    def __init__(self, zi:Composition, p_max:float, temp_min, temp_max, temp_step,p_min = 0.1):
        self.zi = zi.composition

        self.p_min = p_min
        self.p_max = p_max
        self.p_i = self.p_max / 2
    
        # Здесь определили диапазон температур
        self.temp_range = np.arange(start=temp_min + 273.14, stop= temp_max + 273.14, step= temp_step)


## Часть алгоритма для расчета Pb
    def define_s_sp(self, p, t):
        '''
        метод позволяет определить соотношения Sv и Sl при заданных PT.
        Вспомогательный метод для алгоритма
        
        '''
        phase_stability = PhaseStability(self.zi, p, t)

        if (phase_stability.S_l - 1) < 10 ** -5:
            if (phase_stability.S_v) < 10 ** -5:
                y_sp = {}
                for component in self.zi.keys():
                    y_sp[component] = 0
                k_sp = None
                r_sp = None
                letuch_z = None
                letuch_sp = None

        
        if phase_stability.S_l > 1:
            if phase_stability.S_l > phase_stability.S_v:
                k_sp = phase_stability.k_values_liquid
                r_sp = phase_stability.ri_l
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_sp = phase_stability.liquid_eos.fugacity_by_roots[phase_stability.liquid_eos.choosen_eos_root]
                y_sp = {}
                for component in self.zi.keys():
                    y_sp[component] = self.zi[component] / phase_stability.k_values_liquid[component]
            
            else:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_sp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_sp = {}
                for component in self.zi.keys():
                    y_sp[component] = self.zi[component] * phase_stability.k_values_vapour[component]
        
        else:
                if phase_stability.S_v < 1:
                    y_sp = {}
                    for component in self.zi.keys():
                        y_sp[component] = 0
                    k_sp = None
                    r_sp = None
                    letuch_z = None
                    letuch_sp = None

        if phase_stability.S_v > 1:
            if phase_stability.S_v > phase_stability.S_l:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_sp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_sp = {}
                for component in self.zi.keys():
                    y_sp[component] = self.zi[component] * phase_stability.k_values_vapour[component]
            
            else:
                if phase_stability.S_l < 1:
                    y_sp = {}
                    for component in self.zi.keys():
                        y_sp[component] = 0
                    k_sp = None
                    r_sp = None
                    letuch_z = None
                    letuch_sp = None

        S_sp = sum(y_sp.values())
        #print(S_sp)
        print(f'S_v: {phase_stability.S_v}, S_l: {phase_stability.S_l}')
        print(phase_stability.stable)
        return {'s_sp':S_sp, 'y_sp':y_sp, 'k_sp':k_sp, 'r_sp':r_sp, 'letuch_sp':letuch_sp, 'letuch_z': letuch_z}


    def main_loop_sp(self, t, lambd = 1):
        cur_s_sp = self.define_s_sp(self.p_i, t =t)

        # Если s_sp 0, то обновляем давление
        while cur_s_sp['s_sp'] == 0:
            print(self.p_i)
            self.p_max = self.p_i
            self.p_i = (self.p_max + self.p_min) / 2
            
            # Проверка на то, что P_max и P_min не равны друг другу
            if self.p_max - self.p_min == math.pow(10,-8):
                print('P_max и P_min равны, давление насыщения не найдено!!!')
            
            # Считаем s_sp еще раз
            else:
                cur_s_sp = self.define_s_sp(self.p_i, t)
                print(self.p_i)
        # если ssp не ноль, то начинается цикл  расчета Pb
        else:

            # не разобрался зачем это есть в вба
            r_sp1 = cur_s_sp['r_sp']


            r_sp = {}
            for component in cur_s_sp['letuch_z'].keys():
                r_sp[component] = math.exp(cur_s_sp['letuch_z'][component]) / (math.exp(cur_s_sp['letuch_sp'][component]) * cur_s_sp['s_sp'])
            
            y_sp = {}
            for component in r_sp.keys():
                y_sp[component] = cur_s_sp['y_sp'][component] * math.pow(r_sp[component], lambd)
            print(f'y_sp: {y_sp}')

            
            self.sum_y_sp = sum(y_sp.values())
            print(f'sum_y_sp: {self.sum_y_sp}')
            print(f'sum_y_sp-1: {abs(self.sum_y_sp - 1)}')



            #строки с 559 в вба
            self.Sum = []
            for component in self.zi:
                self.Sum.append(math.log(r_sp[component]) / math.log(y_sp[component]) / self.zi[component])
            self.Sum = sum(self.Sum)

            self.Ykz = []
            for component in self.zi:
                self.Ykz.append(y_sp[component] / self.zi[component])
            self.Ykz = sum(self.Ykz)

            if abs(1 - self.sum_y_sp) < math.pow(10, -3):
                print(f'Pb найдено: {self.p_i}')

            elif math.pow(self.Ykz,2) < math.pow(10,-3):
                print(f'Pb найдено: {self.p_i}')

            else:
                print(self.p_i)
                self.p_min = self.p_i
                self.p_i = (self.p_max + self.p_min) / 2
                print('Pb не найдено')
                print(cur_s_sp)
                print(self.p_i)


    def loop_v2(self, t):
        self.main_loop_sp(t)
        
        while ((abs(1 - self.sum_y_sp) < math.pow(10, -3)) == False) and ((math.pow(self.Ykz,2) < math.pow(10,-3)) == False):
            self.main_loop_sp(t)
        
        self.p_i = self.p_i / 2



## Часть алгоритма для расчета Pdew

    def define_s_dp(self, p, t):
        '''
        метод позволяет определить соотношения Sv и Sl при заданных PT.
        Вспомогательный метод для алгоритма
        
        '''
        phase_stability = PhaseStability(self.zi, p, t)

        if (phase_stability.S_l - 1) < 10 ** -5:
            if (phase_stability.S_v) < 10 ** -5:
                y_dp = {}
                for component in self.zi.keys():
                    y_dp[component] = 0
                k_dp = None
                r_dp = None
                letuch_z = None
                letuch_dp = None

        
        if phase_stability.S_l > 1:
            if phase_stability.S_l > phase_stability.S_v:
                k_dp = phase_stability.k_values_liquid
                r_dp = phase_stability.ri_l
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_dp = phase_stability.liquid_eos.fugacity_by_roots[phase_stability.liquid_eos.choosen_eos_root]
                y_dp = {}
                for component in self.zi.keys():
                    y_dp[component] = self.zi[component] / phase_stability.k_values_liquid[component]
            
            else:
                k_dp = phase_stability.k_values_vapour
                r_dp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_dp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_dp = {}
                for component in self.zi.keys():
                    y_dp[component] = self.zi[component] * phase_stability.k_values_vapour[component]
        
        else:
                if phase_stability.S_v < 1:
                    y_dp = {}
                    for component in self.zi.keys():
                        y_dp[component] = 0
                    k_dp = None
                    r_dp = None
                    letuch_z = None
                    letuch_dp = None

        if phase_stability.S_v > 1:
            if phase_stability.S_v > phase_stability.S_l:
                k_dp = phase_stability.k_values_vapour
                r_dp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_dp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_dp = {}
                for component in self.zi.keys():
                    y_dp[component] = self.zi[component] * phase_stability.k_values_vapour[component]
            
            else:
                if phase_stability.S_l < 1:
                    y_dp = {}
                    for component in self.zi.keys():
                        y_dp[component] = 0
                    k_dp = None
                    r_dp = None
                    letuch_z = None
                    letuch_dp = None

        S_dp = sum(y_dp.values())
        #print(S_sp)
        print(f'S_v: {phase_stability.S_v}, S_l: {phase_stability.S_l}')
        print(phase_stability.stable)
        return {'s_dp':S_dp, 'y_dp':y_dp, 'k_dp':k_dp, 'r_dp':r_dp, 'letuch_dp':letuch_dp, 'letuch_z': letuch_z}

    def main_loop_dp(self, t, lambd = 1):
        self.p_min = 0.1
        
        #TODO: Проблема в этом. Пробуем исправить подменой Pi после определения Pb
        #self.p_i = self.p_i / 2
        
        cur_s_dp = self.define_s_dp(self.p_i, t =t)

        # Если s_dp 0, то обновляем давление
        while cur_s_dp['s_dp'] == 0:
            print(self.p_i)
            self.p_min = self.p_i
            self.p_i = (self.p_max + self.p_min) / 2
            
            # Проверка на то, что P_max и P_min не равны друг другу
            if self.p_max - self.p_min == math.pow(10,-8):
                print('P_max и P_min равны, давление насыщения не найдено!!!')
            
            # Считаем s_sp еще раз
            else:
                cur_s_dp = self.define_s_dp(self.p_i, t)
                print(self.p_i)
        # если ssp не ноль, то начинается цикл  расчета Pdew
        else:

            # не разобрался зачем это есть в вба
            r_sp1 = cur_s_dp['r_dp']


            r_dp = {}
            for component in cur_s_dp['letuch_z'].keys():
                r_dp[component] = math.exp(cur_s_dp['letuch_z'][component]) / (math.exp(cur_s_dp['letuch_dp'][component]) * cur_s_dp['s_dp'])
            
            y_dp = {}
            for component in r_dp.keys():
                y_dp[component] = cur_s_dp['y_dp'][component] * math.pow(r_dp[component], lambd)
            print(f'y_dp: {y_dp}')

            
            self.sum_y_dp = sum(y_dp.values())
            print(f'sum_y_dp: {self.sum_y_dp}')
            print(f'sum_y_dp-1: {abs(self.sum_y_dp - 1)}')



            #строки с 559 в вба
            self.Sum_dp = []
            for component in self.zi:
                self.Sum_dp.append(math.log(r_dp[component]) / math.log(y_dp[component]) / self.zi[component])
            self.Sum_dp = sum(self.Sum_dp)

            self.Ykz_dp = []
            for component in self.zi:
                self.Ykz_dp.append(y_dp[component] / self.zi[component])
            self.Ykz_dp = sum(self.Ykz_dp)

            if abs(1 - self.sum_y_dp) < math.pow(10, -3):
                print(f'Pdew найдено: {self.p_i}')

            elif math.pow(self.Ykz_dp,2) < math.pow(10,-3):
                print(f'Pdew найдено: {self.p_i}')

            else:
                print(self.p_i)
                self.p_max = self.p_i
                self.p_i = (self.p_max + self.p_min) / 2
                print('Pdew не найдено')
                print(cur_s_dp)
                print(self.p_i)

    def loop_v2_dew(self, t):
        self.main_loop_dp(t)
        
        while ((abs(1 - self.sum_y_dp) < math.pow(10, -3)) == False) and ((math.pow(self.Ykz_dp,2) < math.pow(10,-3)) == False):
            self.main_loop_dp(t)


    def main_loop_phase_diagram(self):
        for temp in self.temp_range:
            



if __name__ == '__main__':
    comosition = Composition({'C1': 0.6, 'nC4':0.4})
    phase_diag = PhaseDiagram(comosition, 40, temp_min=0, temp_max= 120, temp_step= 10)
    phase_diag.loop_v2(320) 
    phase_diag.loop_v2_dew(320)


