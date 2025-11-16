import math as math
from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition
from calculations.Utils.Constants import TOL_SAT_PRESSURE


class SaturationPressureCalculation:
    def __init__(self, composition_object: Composition, p_max:float, temp, p_min = 0.1):
        self.zi = composition_object
        self.p_min_bub = p_min
        self.p_max_bub = p_max
        self.p_i = self.p_max_bub / 2

        self.temp = temp + 273.14
        self.results = {}
        

    def calculate_inital_p_sat(self):


        pi_to_summerize = []
        for component in self.composition._composition.keys():
            value = ((self.composition._composition[component] * self.composition._composition_data['critical_pressure'][component]) * 
                     math.exp(5.37 * (1 + self.composition._composition_data['acentric_factor'][component]) * (1 - (self.composition._composition_data['critical_temperature'][component]/self.temp))))
            print(component, value)
            pi_to_summerize.append(value)

        self.init_saturation_pressure_wilson = sum(pi_to_summerize)


    def define_s_sp(self, p, eos:EOS):
        phase_stability = TwoPhaseStabilityTest(self.zi, p, self.temp, eos)
        phase_stability.calculate_phase_stability()

        if (phase_stability.S_l - 1) < (TOL_SAT_PRESSURE) and (phase_stability.S_v - 1) < (TOL_SAT_PRESSURE):
            y_sp = {component: 0 for component in self.zi._composition.keys()}
            return {'s_sp': 0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None, 
                    'letuch_sp': None, 'letuch_z': None}

        if phase_stability.S_l > 1:
            if phase_stability.S_l > phase_stability.S_v:
                k_sp = phase_stability.k_values_liquid
                r_sp = phase_stability.ri_l
                letuch_z = phase_stability.initial_eos.fugacities
                letuch_sp = phase_stability.liquid_eos.fugacities
                y_sp = {component: self.zi._composition[component] / phase_stability.k_values_liquid[component] 
                        for component in self.zi._composition.keys()}
            else:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacities
                letuch_sp = phase_stability.vapour_eos.fugacities
                y_sp = {component: self.zi._composition[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi._composition.keys()}
        else:
            if phase_stability.S_v < 1:
                y_sp = {component: 0 for component in self.zi._composition.keys()}
                return {'s_sp': 0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None, 
                        'letuch_sp': None, 'letuch_z': None}

        if phase_stability.S_v > 1:
            if phase_stability.S_v > phase_stability.S_l:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.fugacities
                letuch_sp = phase_stability.vapour_eos.fugacities
                y_sp = {component: self.zi._composition[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi._composition.keys()}
            else:
                if phase_stability.S_l < 1:
                    y_sp = {component: 0 for component in self.zi._composition.keys()}
                    return {'s_sp': 0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None, 
                            'letuch_sp': None, 'letuch_z': None}

        S_sp = sum(y_sp.values())
        return {'s_sp': S_sp, 'y_sp': y_sp, 'k_sp': k_sp, 'r_sp': r_sp, 
                'letuch_sp': letuch_sp, 'letuch_z': letuch_z}


    def sp_process(self, eos:EOS, lambd=1):
        cur_s_sp = self.define_s_sp(self.p_i, eos)

        # Если s_sp 0, то обновляем давление
        while cur_s_sp['s_sp'] == 0:
            self.p_max_bub = self.p_i
            self.p_i = (self.p_max_bub + self.p_min_bub) / 2
            
            # Проверка на отсутствие решения
            if self.p_max_bub - self.p_min_bub < TOL_SAT_PRESSURE:
                return None
            
            cur_s_sp = self.define_s_sp(self.p_i, eos)

        # если ssp не ноль, то начинается цикл расчета Pb
        r_sp = {}
        for component in cur_s_sp['letuch_z'].keys():
            r_sp[component] = math.exp(cur_s_sp['letuch_z'][component]) / (
                math.exp(cur_s_sp['letuch_sp'][component]) * cur_s_sp['s_sp'])
        
        y_sp = {component: cur_s_sp['y_sp'][component] * math.pow(r_sp[component], lambd) 
                for component in r_sp.keys()}

        self.sum_y_sp = sum(y_sp.values())

        self.Sum = sum(math.log(r_sp[component]) / math.log(y_sp[component] / self.zi._composition[component]) 
                       for component in self.zi._composition.keys())
        
        self.Ykz = sum(y_sp[component] / self.zi._composition[component] for component in self.zi._composition.keys())

        if (abs(1 - self.sum_y_sp) < TOL_SAT_PRESSURE) or (math.pow(self.Ykz, 2) < TOL_SAT_PRESSURE):
            #print(f'Pb найдено: {self.p_i}')
            pass

        else:
            self.p_min_bub = self.p_i
            self.p_i = (self.p_max_bub + self.p_min_bub) / 2


    def sp_convergence_loop(self, eos:EOS):
        self.sp_process(eos)
        if self.p_max_bub - self.p_min_bub < TOL_SAT_PRESSURE:
            return None
        
        while ((abs(1 - self.sum_y_sp) < math.pow(10, -10)) == False) and ((math.pow(self.Ykz, 2) < math.pow(10, -10)) == False):
            self.sp_process(eos)
            if self.p_max_bub - self.p_min_bub < TOL_SAT_PRESSURE:
                return None

        self.p_b = self.p_i
        self.p_i = self.p_i / 2
        return self.p_b