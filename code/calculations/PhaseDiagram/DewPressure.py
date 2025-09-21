import math as math
from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition

class DewPressureCalculation:
    def __init__(self, composition_object: Composition, p_max:float, temp, p_min = 0.1):
        self.zi = composition_object
        self.p_i = self.p_max_bub / 2
        self.p_min_dew = 0
        self.p_max_dew = p_max  # Инициализация p_max_dew

        self.temp = temp + 273.14
        self.results = {}

    def define_s_dp(self, p, eos: EOS):
        phase_stability = TwoPhaseStabilityTest(self.zi, p, self.temp, eos)
        phase_stability.calculate_phase_stability()

        if (phase_stability.S_l - 1) < 10 ** -5 and (phase_stability.S_v - 1) < 10 ** -5:
            y_dp = {component: 0 for component in self.zi._composition.keys()}
            return {'s_dp': 0, 'y_dp': y_dp, 'k_dp': None, 'r_dp': None, 
                    'letuch_dp': None, 'letuch_z': None}

        if phase_stability.S_l > 1:
            if phase_stability.S_l > phase_stability.S_v:
                k_dp = phase_stability.k_values_liquid
                r_dp = phase_stability.ri_l
                letuch_z = phase_stability.initial_eos.choosen_fugacities
                letuch_dp = phase_stability.liquid_eos.choosen_fugacities
                y_dp = {component: self.zi._composition[component] / phase_stability.k_values_liquid[component] 
                        for component in self.zi._composition.keys()}
            else:
                k_dp = phase_stability.k_values_vapour
                r_dp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.choosen_fugacities
                letuch_dp = phase_stability.vapour_eos.choosen_fugacities
                y_dp = {component: self.zi._composition[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi._composition.keys()}
        else:
            if phase_stability.S_v < 1:
                y_dp = {component: 0 for component in self.zi._composition.keys()}
                return {'s_dp': 0, 'y_dp': y_dp, 'k_dp': None, 'r_dp': None, 
                        'letuch_dp': None, 'letuch_z': None}

        if phase_stability.S_v > 1:
            if phase_stability.S_v > phase_stability.S_l:
                k_dp = phase_stability.k_values_vapour
                r_dp = phase_stability.ri_v
                letuch_z = phase_stability.initial_eos.choosen_fugacities
                letuch_dp = phase_stability.vapour_eos.choosen_fugacities
                y_dp = {component: self.zi._composition[component] * phase_stability.k_values_vapour[component] 
                        for component in self.zi._composition.keys()}
            else:
                if phase_stability.S_l < 1:
                    y_dp = {component: 0 for component in self.zi._composition.keys()}
                    return {'s_dp': 0, 'y_dp': y_dp, 'k_dp': None, 'r_dp': None, 
                            'letuch_dp': None, 'letuch_z': None}

        S_dp = sum(y_dp.values())
        return {'s_dp': S_dp, 'y_dp': y_dp, 'k_dp': k_dp, 'r_dp': r_dp, 
                'letuch_dp': letuch_dp, 'letuch_z': letuch_z}

    def dp_process(self, eos:EOS, lambd=1):
        cur_s_dp = self.define_s_dp(self.p_i, eos)

        # Если s_dp 0, то обновляем давление
        while cur_s_dp['s_dp'] == 0:
            self.p_min_dew = self.p_i
            self.p_i = (self.p_max_dew + self.p_min_dew) / 2
            
            # Проверка на отсутствие решения
            if self.p_max_dew - self.p_min_dew < math.pow(10, -5):
                return None
            
            cur_s_dp = self.define_s_dp(self.p_i, eos)

        # если ssp не ноль, то начинается цикл расчета Pdew
        r_dp = {}
        for component in cur_s_dp['letuch_z'].keys():
            r_dp[component] = math.exp(cur_s_dp['letuch_z'][component]) / (
                math.exp(cur_s_dp['letuch_dp'][component]) * cur_s_dp['s_dp'])
        
        y_dp = {component: cur_s_dp['y_dp'][component] * math.pow(r_dp[component], lambd) 
                for component in r_dp.keys()}

        self.sum_y_dp = sum(y_dp.values())

        self.Sum_dp = sum(math.log(r_dp[component]) / math.log(y_dp[component] / self.zi._composition[component]) 
                          for component in self.zi._composition.keys())
        
        self.Ykz_dp = sum(y_dp[component] / self.zi._composition[component] for component in self.zi._composition.keys())

        if abs(1 - self.sum_y_dp) < math.pow(10, -3) or math.pow(self.Ykz_dp, 2) < math.pow(10, -3):
            print(f'Pdew найдено: {self.p_i}')
        else:
            self.p_max_dew = self.p_i
            self.p_i = (self.p_max_dew + self.p_min_dew) / 2

    def dp_convergence_loop(self, eos):
        self.dp_process(eos)
        if self.p_max_dew - self.p_min_dew < math.pow(10, -5):
            return None
        
        while not (abs(1 - self.sum_y_dp) < math.pow(10, -3) or math.pow(self.Ykz_dp, 2) < math.pow(10, -3)):
            self.dp_process(eos)
            if self.p_max_dew - self.p_min_dew < math.pow(10, -5):
                return None

        self.p_dew = self.p_i
        return self.p_dew