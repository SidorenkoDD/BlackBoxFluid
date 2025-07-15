from Composition import Composition
from Conditions import Conditions
from PhaseStability_v3 import PhaseStability
import numpy as np
import pandas as pd

class PhaseDiagram:

    def __init__(self, zi: Composition, current_conditions: Conditions,  p_start = 1, p_end = 10, p_step = 5,
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

        print(change_intervals)
        return change_intervals
    

    def find_pressure_bisection(self,ranges:list, p,t):
        result = []
        for range in ranges:
            fa = PhaseStability(self.zi, range[0], t)
            fb = PhaseStability(self.zi, range[1], t)
            
            assert fa != fb, "Функция должна иметь разные значения на концах интервала!"

        while pres_tuple[1] - pres_tuple[0] > eps:
            mid = (pres_tuple[1] + pres_tuple[0]) / 2
            f_mid = PhaseStability(self.zi, mid, temperature)
            if f_mid == fa:
                a = mid
            else:
                b = mid
        return (a + b) / 2






    # # Метод для нахождения интервалов давления, в которых происходит фазовый переход при Т=const
    # def find_change_intervals(self, vals: list, bools: list):
    #     change_intervals = []
    #     for i in range(1, len(bools)):
    #         if bools[i] != bools[i-1]:
    #             change_intervals.append((vals[i-1], vals[i]))
    #     return change_intervals



    def find_threshold(self, pres_tuple: tuple, temperature, eps=1e-6):
    # Проверяем, что на концах интервала значения разные
        fa = PhaseStability(self.zi, pres_tuple[0], temperature)
        fb = PhaseStability(self.zi, pres_tuple[1], temperature)
        assert fa != fb # "Функция должна иметь разные значения на концах интервала!"
        
        while pres_tuple[1] - pres_tuple[0] > eps:
            mid = (pres_tuple[1] + pres_tuple[0]) / 2
            f_mid = PhaseStability(self.zi, mid, temperature)
            if f_mid == fa:
                a = mid
            else:
                b = mid
        return (a + b) / 2


    def calc_phase_diagram(self):
        stability_bools = []
        for temp in self.space_temperature:
            for pres in self.space_pressure:
                stability_obj =  PhaseStability(self.zi, pres, temp)
                stability_bools.append(stability_obj.stable)

            intervals_for_find_p = self.find_change_intervals(self.space_pressure, stability_bools)
            print(self.find_threshold(intervals_for_find_p, temp))
        return stability_bools


if __name__ == '__main__':
    comp = Composition({'C1': 0.3, 'nC4': 0.7})
    cond = Conditions(2, 40)
    phs_diag = PhaseDiagram(comp.composition, cond ,t_start=80, t_end=80, t_step=1)

    phs_diag.find_stability_for_each_pressure_with_constant_t(350)
    
