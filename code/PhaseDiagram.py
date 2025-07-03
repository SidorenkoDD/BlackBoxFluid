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



    # Метод для нахождения интервалов давления, в которых происходит фазовый переход при Т=const
    def find_change_intervals(self, vals: list, bools: list):
        change_intervals = []
        for i in range(1, len(bools)):
            if bools[i] != bools[i-1]:
                change_intervals.append((vals[i-1], vals[i]))
        return change_intervals



    def find_threshold(self, pres_tuple: tuple, temperature, eps=1e-6):
    # Проверяем, что на концах интервала значения разные
        fa = PhaseStability(self.zi, pres_tuple[0], temperature)
        fb = PhaseStability(self.zi, pres_tuple[1], temperature)
        assert fa != fb, "Функция должна иметь разные значения на концах интервала!"

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
        return stability_bools


if __name__ == '__main__':
    comp = Composition({'C1': 0.3, 'nC4': 0.7})
    cond = Conditions(2, 40)
    phs_diag = PhaseDiagram(comp.composition, cond ,t_start=80, t_end=80, t_step=1)
    print(phs_diag.space_pressure, phs_diag.space_temperature)
    print(phs_diag.calc_phase_diagram())
    print(phs_diag.find_change_intervals(phs_diag.space_pressure, phs_diag.calc_phase_diagram()))
