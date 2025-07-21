from Composition import Composition
from PhaseStability_v3 import PhaseStability
import math as math
import numpy as np
import matplotlib.pyplot as plt


class SaturationPressure:

    def __init__(self, zi, p_max:float, temp, p_min = 0.1):
        self.zi = zi
        self.p_min = p_min
        self.p_max = p_max
        self.p_i = self.p_max / 2
        self.temp = temp
        self.failed = False  # Флаг для отслеживания неудачных расчетов
    

    def define_s_sp(self, p):
        '''
        метод позволяет определить соотношения Sv и Sl при заданных PT.
        Вспомогательный метод для алгоритма
        '''
        phase_stability = PhaseStability(self.zi, p, self.temp)

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
        return {'s_sp':S_sp, 'y_sp':y_sp, 'k_sp':k_sp, 'r_sp':r_sp, 'letuch_sp':letuch_sp, 'letuch_z': letuch_z}

    def check_pressure_diff(self):
        return (self.p_max - self.p_min) > math.pow(10,-5)

    def sp_process(self, lambd = 1):
        cur_s_sp = self.define_s_sp(self.p_i)

        # Если s_sp 0, то обновляем давление
        while cur_s_sp['s_sp'] == 0:
            self.p_max = self.p_i
            self.p_i = (self.p_max + self.p_min) / 2
            
            # Проверка на разницу давлений
            if self.p_max - self.p_min < math.pow(10,-5):
                print('P_max и P_min равны, давление насыщения не найдено!!!')
                self.failed = True
                return
            else:
                cur_s_sp = self.define_s_sp(self.p_i)

        # Расчет давления насыщения
        r_sp1 = cur_s_sp['r_sp']
        r_sp = {}
        for component in cur_s_sp['letuch_z'].keys():
            r_sp[component] = math.exp(cur_s_sp['letuch_z'][component]) / (math.exp(cur_s_sp['letuch_sp'][component]) * cur_s_sp['s_sp'])
        
        y_sp = {}
        for component in r_sp.keys():
            y_sp[component] = cur_s_sp['y_sp'][component] * math.pow(r_sp[component], lambd)
        
        self.sum_y_sp = sum(y_sp.values())
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
            self.p_min = self.p_i
            self.p_i = (self.p_max + self.p_min) / 2

    def sp_convergence_loop(self):
        if not self.check_pressure_diff():
            return None
            
        self.failed = False
        self.sp_process()
        if self.failed:
            return None
            
        while ((abs(1 - self.sum_y_sp) >= math.pow(10, -3)) and (math.pow(self.Ykz,2) >= math.pow(10,-3))):
            self.sp_process()
            if self.failed:
                return None

        self.p_b = self.p_i
        self.p_i = self.p_i / 2
        return self.p_b

    def define_s_dp(self, p):
        '''
        метод позволяет определить соотношения Sv и Sl при заданных PT.
        Вспомогательный метод для алгоритма
        '''
        phase_stability = PhaseStability(self.zi, p, self.temp)

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
        return {'s_dp':S_dp, 'y_dp':y_dp, 'k_dp':k_dp, 'r_dp':r_dp, 'letuch_dp':letuch_dp, 'letuch_z': letuch_z}

    def dp_process(self, lambd = 1):
        self.p_min = 0.1
        cur_s_dp = self.define_s_dp(self.p_i)

        # Если s_dp 0, то обновляем давление
        while cur_s_dp['s_dp'] == 0:
            self.p_min = self.p_i
            self.p_i = (self.p_max + self.p_min) / 2
            
            # Проверка на разницу давлений
            if self.p_max - self.p_min < math.pow(10,-5):
                print('P_max и P_min равны, давление конденсации не найдено!!!')
                self.failed = True
                return
            else:
                cur_s_dp = self.define_s_dp(self.p_i)

        # Расчет давления конденсации
        r_sp1 = cur_s_dp['r_dp']
        r_dp = {}
        for component in cur_s_dp['letuch_z'].keys():
            r_dp[component] = math.exp(cur_s_dp['letuch_z'][component]) / (math.exp(cur_s_dp['letuch_dp'][component]) * cur_s_dp['s_dp'])
        
        y_dp = {}
        for component in r_dp.keys():
            y_dp[component] = cur_s_dp['y_dp'][component] * math.pow(r_dp[component], lambd)

        self.sum_y_dp = sum(y_dp.values())
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
            self.p_max = self.p_i
            self.p_i = (self.p_max + self.p_min) / 2

    def dp_convergence_loop(self):
        if not self.check_pressure_diff():
            return None
            
        self.failed = False
        self.dp_process()
        if self.failed:
            return None
            
        while (abs(1 - self.sum_y_dp) >= math.pow(10, -3)) and (math.pow(self.Ykz_dp,2) >= math.pow(10,-3)):
            self.dp_process()
            if self.failed:
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
        print(self.results)

    def plot_phase_diagram(self):
        x = []
        y = []
        # Фильтрация None значений
        for temp, pressures in self.results.items():
            for p in pressures:
                if p is not None:  # Игнорируем None
                    x.append(temp)
                    y.append(p)
        plt.scatter(x, y)
        plt.xlabel('Temperature (K)')
        plt.ylabel('Pressure (bar)')
        plt.title('Phase Diagram')
        plt.show()

    def plot_phase_diagram_v2(self):
        bubble_points = []
        dew_points = []
        temperatures = []
        
        for temp, (pb, pdew) in self.results.items():
            t_celsius = temp - 273.15
            if pb is not None:
                bubble_points.append(pb)
                temperatures.append(t_celsius)
            if pdew is not None:
                dew_points.append(pdew)
        
        # Убедимся, что у нас есть данные для построения
        if not bubble_points and not dew_points:
            print("Нет данных для построения фазовой диаграммы")
            return
        
        # Создаем график
        plt.figure(figsize=(10, 6))
        
        # Точки линии пузырьков
        if bubble_points:
            # Сортируем по температуре
            sorted_data = sorted(zip(temperatures, bubble_points))
            sorted_temps, sorted_pbs = zip(*sorted_data)
            plt.plot(sorted_temps, sorted_pbs, 'bo-', label='Линия пузырьков (Pb)')
        
        # Точки линии росы
        if dew_points:
            # Используем те же температуры, что и для линии пузырьков
            sorted_data = sorted(zip(temperatures, dew_points))
            sorted_temps, sorted_dews = zip(*sorted_data)
            plt.plot(sorted_temps, sorted_dews, 'ro-', label='Линия росы (Pdew)')
        
        plt.xlabel('Температура (°C)')
        plt.ylabel('Давление (бар)')
        plt.title('Фазовая диаграмма')
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    comosition = Composition({'C1': 0.6, 'C6':0.4})
    phase_diag = PhaseDiagram(comosition, 40, 0, 140, 5)
    phase_diag.calc_phase_diagram()
    phase_diag.plot_phase_diagram_v2()