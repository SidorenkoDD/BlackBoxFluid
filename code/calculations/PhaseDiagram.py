from Composition import Composition
from Conditions import Conditions
from PhaseStability_v3 import PhaseStability
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class PhaseDiagram:

    def __init__(self, zi: Composition, current_conditions: Conditions,  p_start = 1, p_end = 20, p_step = 20,
                 t_start = 20, t_end = 200, t_step = 5):
        
        self.zi = zi
        self.current_conditions = current_conditions


        self.p_start = p_start
        self.p_end = p_end
        self.p_step = p_step

        self.t_end = t_end + 273.14
        self.t_start = t_start + 273.14
        self.t_step = t_step

        self.space_pressure = np.linspace(p_start, p_end, p_step)
        self.space_temperature = np.linspace(self.t_start, self.t_end, t_step)


    def find_chage_intervals_for_each_pressure_with_constant_t(self, t):
        bool_results = []
        for p in self.space_pressure:
            phase_stability = PhaseStability(self.zi, p, t)
            bool_results.append(phase_stability.stable)

        print(self.space_pressure)
        print(bool_results)
        change_intervals = []
        for i in range(1, len(bool_results)):
            if bool_results[i] != bool_results[i-1]:
                change_intervals.append((self.space_pressure[i-1], self.space_pressure[i]))

        #print(change_intervals)
        return change_intervals
    



    def find_pressure_bisection_test(self, change_intervals: list, t, eps=1e-3):
        """
        Находит точки изменения стабильности системы методом бисекции.
        
        Parameters:
        - change_intervals: список интервалов, где происходит изменение stable
        - t: температура (в Кельвинах)
        - eps: точность определения точки перехода
        
        Returns:
        - Список давлений, при которых происходит смена stable
        """
        transition_points = []
        
        for interval in change_intervals:
            a, b = interval
            # Проверяем значения на концах интервала
            fa = PhaseStability(self.zi, a, t).stable
            fb = PhaseStability(self.zi, b, t).stable
            
            if fa == fb:
                continue  # пропускаем интервалы без изменения stable
                
            # Ищем точку перехода методом бисекции
            while b - a > eps:
                mid = (a + b) / 2
                f_mid = PhaseStability(self.zi, mid, t).stable
                
                if f_mid == fa:
                    a = mid
                else:
                    b = mid
            
            # Добавляем найденную точку перехода
            transition_points.append((a + b) / 2)
        print(transition_points)
        return transition_points


 


    def calc_phase_diagram(self):
        result_data_for_phase_diagram = {}
        for temp in self.space_temperature:
            change_intervals = self.find_chage_intervals_for_each_pressure_with_constant_t(temp)
            result_data_for_phase_diagram[temp] = self.find_pressure_bisection_test(change_intervals=change_intervals, t= temp)
        self.result_data_for_phase_diagram = result_data_for_phase_diagram
        return self.result_data_for_phase_diagram


    def plot_phase_diagram(self):
        x = []
        y = []

        # Заполняем списки
        for key, values in self.result_data_for_phase_diagram.items():
            for value in values:
                x.append(key)
                y.append(value)

        print(x)
        print(y)
        plt.scatter(x, y)  # Точечный график
        #plt.plot(x, y)     # Линейный график (если нужен)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('График данных')
        plt.show()

if __name__ == '__main__':
    comp = Composition({'C1': 0.4, 'C6':0.6})
    cond = Conditions(2, 40)
    phs_diag = PhaseDiagram(comp.composition, cond,
                            p_start= 0.1, p_end= 40, p_step=10,
                            t_start=-250, t_end=250, t_step=10)

    # change_intervals = phs_diag.find_chage_intervals_for_each_pressure_with_constant_t(523.14)
    # print(change_intervals)
    # phs_diag.find_pressure_bisection_test(change_intervals=change_intervals, t = 523.14)

    print(phs_diag.calc_phase_diagram())
    phs_diag.plot_phase_diagram()



    
