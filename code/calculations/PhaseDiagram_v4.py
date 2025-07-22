from Composition import Composition
from PhaseStability_v3 import PhaseStability
import math as math
import numpy as np
import matplotlib.pyplot as plt


class SaturationPressure:

    def __init__(self, zi, p_max:float, temp, p_min = 0.1):
        self.zi = zi
        self.p_min_bub = p_min
        self.p_max_bub = p_max
        self.p_i = self.p_max_bub / 2
        self.p_min_dew = 0
        self.p_max_dew = p_max  # Инициализация p_max_dew
        self.temp = temp
        self.results = {}
    

    def define_s_sp(self, p):
        phase_stability = PhaseStability(self.zi, p, self.temp)

        if (phase_stability.S_l - 1) < 10 ** -5 and (phase_stability.S_v) < 10 ** -5:
            y_sp = {component: 0 for component in self.zi.keys()}
            return {'s_sp': 0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None, 
                    'letuch_sp': None, 'letuch_z': None}

        if phase_stability.S_l > 1:
            if phase_stability.S_l > phase_stability.S_v:
                k_sp = phase_stability.k_values_liquid
                r_sp = phase_stability.ri_l
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_sp = phase_stability.liquid_eos.fugacity_by_roots[phase_stability.liquid_eos.choosen_eos_root]
                y_sp = {component: self.zi[component] / phase_stability.k_values_liquid[component] 
                        for component in self.zi.keys()}
            else:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_sp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_sp = {component: self.zi[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi.keys()}
        else:
            if phase_stability.S_v < 1:
                y_sp = {component: 0 for component in self.zi.keys()}
                return {'s_sp': 0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None, 
                        'letuch_sp': None, 'letuch_z': None}

        if phase_stability.S_v > 1:
            if phase_stability.S_v > phase_stability.S_l:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_sp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_sp = {component: self.zi[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi.keys()}
            else:
                if phase_stability.S_l < 1:
                    y_sp = {component: 0 for component in self.zi.keys()}
                    return {'s_sp': 0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None, 
                            'letuch_sp': None, 'letuch_z': None}

        S_sp = sum(y_sp.values())
        return {'s_sp': S_sp, 'y_sp': y_sp, 'k_sp': k_sp, 'r_sp': r_sp, 
                'letuch_sp': letuch_sp, 'letuch_z': letuch_z}

    def sp_process(self, lambd=1):
        cur_s_sp = self.define_s_sp(self.p_i)

        # Если s_sp 0, то обновляем давление
        while cur_s_sp['s_sp'] == 0:
            self.p_max_bub = self.p_i
            self.p_i = (self.p_max_bub + self.p_min_bub) / 2
            
            # Проверка на отсутствие решения
            if self.p_max_bub - self.p_min_bub < math.pow(10, -5):
                return None
            
            cur_s_sp = self.define_s_sp(self.p_i)

        # если ssp не ноль, то начинается цикл расчета Pb
        r_sp = {}
        for component in cur_s_sp['letuch_z'].keys():
            r_sp[component] = math.exp(cur_s_sp['letuch_z'][component]) / (
                math.exp(cur_s_sp['letuch_sp'][component]) * cur_s_sp['s_sp'])
        
        y_sp = {component: cur_s_sp['y_sp'][component] * math.pow(r_sp[component], lambd) 
                for component in r_sp.keys()}

        self.sum_y_sp = sum(y_sp.values())

        self.Sum = sum(math.log(r_sp[component]) / math.log(y_sp[component]) / self.zi[component] 
                       for component in self.zi)
        
        self.Ykz = sum(y_sp[component] / self.zi[component] for component in self.zi)

        if abs(1 - self.sum_y_sp) < math.pow(10, -3) or math.pow(self.Ykz, 2) < math.pow(10, -3):
            print(f'Pb найдено: {self.p_i}')
        else:
            self.p_min_bub = self.p_i
            self.p_i = (self.p_max_bub + self.p_min_bub) / 2

    def sp_convergence_loop(self):
        self.sp_process()
        if self.p_max_bub - self.p_min_bub < math.pow(10, -5):
            return None
        
        while not (abs(1 - self.sum_y_sp) < math.pow(10, -3) or math.pow(self.Ykz, 2) < math.pow(10, -3)):
            self.sp_process()
            if self.p_max_bub - self.p_min_bub < math.pow(10, -5):
                return None

        self.p_b = self.p_i
        self.p_i = self.p_i / 2
        return self.p_b

    def define_s_dp(self, p):
        phase_stability = PhaseStability(self.zi, p, self.temp)

        if (phase_stability.S_l - 1) < 10 ** -5 and (phase_stability.S_v) < 10 ** -5:
            y_dp = {component: 0 for component in self.zi.keys()}
            return {'s_dp': 0, 'y_dp': y_dp, 'k_dp': None, 'r_dp': None, 
                    'letuch_dp': None, 'letuch_z': None}

        if phase_stability.S_l > 1:
            if phase_stability.S_l > phase_stability.S_v:
                k_dp = phase_stability.k_values_liquid
                r_dp = phase_stability.ri_l
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_dp = phase_stability.liquid_eos.fugacity_by_roots[phase_stability.liquid_eos.choosen_eos_root]
                y_dp = {component: self.zi[component] / phase_stability.k_values_liquid[component] 
                        for component in self.zi.keys()}
            else:
                k_dp = phase_stability.k_values_vapour
                r_dp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_dp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_dp = {component: self.zi[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi.keys()}
        else:
            if phase_stability.S_v < 1:
                y_dp = {component: 0 for component in self.zi.keys()}
                return {'s_dp': 0, 'y_dp': y_dp, 'k_dp': None, 'r_dp': None, 
                        'letuch_dp': None, 'letuch_z': None}

        if phase_stability.S_v > 1:
            if phase_stability.S_v > phase_stability.S_l:
                k_dp = phase_stability.k_values_vapour
                r_dp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacity_by_roots[phase_stability.initial_eos.choosen_eos_root]
                letuch_dp = phase_stability.vapour_eos.fugacity_by_roots[phase_stability.vapour_eos.choosen_eos_root]
                y_dp = {component: self.zi[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi.keys()}
            else:
                if phase_stability.S_l < 1:
                    y_dp = {component: 0 for component in self.zi.keys()}
                    return {'s_dp': 0, 'y_dp': y_dp, 'k_dp': None, 'r_dp': None, 
                            'letuch_dp': None, 'letuch_z': None}

        S_dp = sum(y_dp.values())
        return {'s_dp': S_dp, 'y_dp': y_dp, 'k_dp': k_dp, 'r_dp': r_dp, 
                'letuch_dp': letuch_dp, 'letuch_z': letuch_z}

    def dp_process(self, lambd=1):
        cur_s_dp = self.define_s_dp(self.p_i)

        # Если s_dp 0, то обновляем давление
        while cur_s_dp['s_dp'] == 0:
            self.p_min_dew = self.p_i
            self.p_i = (self.p_max_dew + self.p_min_dew) / 2
            
            # Проверка на отсутствие решения
            if self.p_max_dew - self.p_min_dew < math.pow(10, -5):
                return None
            
            cur_s_dp = self.define_s_dp(self.p_i)

        # если ssp не ноль, то начинается цикл расчета Pdew
        r_dp = {}
        for component in cur_s_dp['letuch_z'].keys():
            r_dp[component] = math.exp(cur_s_dp['letuch_z'][component]) / (
                math.exp(cur_s_dp['letuch_dp'][component]) * cur_s_dp['s_dp'])
        
        y_dp = {component: cur_s_dp['y_dp'][component] * math.pow(r_dp[component], lambd) 
                for component in r_dp.keys()}

        self.sum_y_dp = sum(y_dp.values())

        self.Sum_dp = sum(math.log(r_dp[component]) / math.log(y_dp[component]) / self.zi[component] 
                          for component in self.zi)
        
        self.Ykz_dp = sum(y_dp[component] / self.zi[component] for component in self.zi)

        if abs(1 - self.sum_y_dp) < math.pow(10, -3) or math.pow(self.Ykz_dp, 2) < math.pow(10, -3):
            print(f'Pdew найдено: {self.p_i}')
        else:
            self.p_max_dew = self.p_i
            self.p_i = (self.p_max_dew + self.p_min_dew) / 2

    def dp_convergence_loop(self):
        self.dp_process()
        if self.p_max_dew - self.p_min_dew < math.pow(10, -5):
            return None
        
        while not (abs(1 - self.sum_y_dp) < math.pow(10, -3) or math.pow(self.Ykz_dp, 2) < math.pow(10, -3)):
            self.dp_process()
            if self.p_max_dew - self.p_min_dew < math.pow(10, -5):
                return None

        self.p_dew = self.p_i
        return self.p_dew


class PhaseDiagram:
    def __init__(self, zi: Composition, p_max, t_min, t_max, t_step):
        self.zi = zi.composition
        self.p_max = p_max
        self.t_min = t_min
        self.t_max = t_max
        self.t_step = t_step
        self.temp_arange = np.arange(self.t_min + 273.14, self.t_max + 273.14, self.t_step)
        self.results = {}

    def calc_phase_diagram(self):
        for temp in self.temp_arange:
            cur_saturation_pressure = SaturationPressure(self.zi, self.p_max, temp)
            pb = cur_saturation_pressure.sp_convergence_loop()
            pdew = cur_saturation_pressure.dp_convergence_loop()
            self.results[temp] = [pb, pdew]
            print(f"Temp: {temp-273.14:.2f}°C, Pb: {pb}, Pdew: {pdew}")

    def plot_phase_diagram(self):
        bubble_points = []
        dew_points = []
        temps = []
        
        for temp, (pb, pdew) in self.results.items():
            temps.append(temp - 273.14)  # Конвертируем обратно в °C
            bubble_points.append(pb if pb is not None else np.nan)
            dew_points.append(pdew if pdew is not None else np.nan)
        
        plt.figure(figsize=(10, 6))
        
        # Фильтруем значения None, заменяя их на np.nan для корректного отображения
        bubble_points = np.array(bubble_points)
        dew_points = np.array(dew_points)
        
        # Рисуем кривые, пропуская np.nan значения
        plt.plot(temps, bubble_points, 'b-', label='Bubble Point')
        plt.plot(temps, dew_points, 'r-', label='Dew Point')
        
        # Отмечаем точки
        plt.scatter(temps, bubble_points, c='blue', marker='o')
        plt.scatter(temps, dew_points, c='red', marker='o')
        
        
        print(temps)
        print('====')
        print(bubble_points)
        print('====')
        print(dew_points)


        plt.xlabel('Temperature (°C)')
        plt.ylabel('Pressure (MPa)')
        plt.title('Phase Diagram')
        plt.legend()
        plt.grid(True)
        plt.xlim(min(temps) - 20, max(temps) + 20)
        plt.ylim(0, self.p_max)
        plt.show()


if __name__ == '__main__':
    composition = Composition({'C1': 0.4, 'C2': 0.2,  'nC4': 0.1,  'C6': 0.3})
    phase_diag = PhaseDiagram(composition, 40, 0, 200, 10)
    phase_diag.calc_phase_diagram()
    phase_diag.plot_phase_diagram()