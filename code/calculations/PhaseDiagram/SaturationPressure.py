import math
from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition

class SaturationPressureCalculation:
    def __init__(self, composition_object: Composition, p_max: float, temp, p_min=0.1):
        self.zi = composition_object
        self.p_min = p_min
        self.p_max = p_max
        self.p_current = (p_max + p_min) / 2
        self.temp = temp + 273.14
        self.results = {}

    def define_s_sp(self, p, eos: EOS):
        """Расчет S_sp и y_sp - ТОЧНО по VBA логике"""
        phase_stability = TwoPhaseStabilityTest(self.zi, p, self.temp, eos)
        phase_stability.calculate_phase_stability()

        Sl = phase_stability.S_l
        Sv = phase_stability.S_v
        letuch_z = phase_stability.initial_eos.fugacities  # ← ВСЕГДА сохраняем!
        
        # БЛОК 1: ТОЧНО VBA - ВЛОЖЕННЫЕ условия (НЕ and!)
        if (Sl - 1) < 1e-5:
            if (Sv - 1) < 1e-5:
                y_sp = {comp: 0.0 for comp in self.zi._composition.keys()}
                return {'s_sp': 0.0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None,
                       'letuch_sp': None, 'letuch_z': letuch_z}  # ← letuch_z НЕ None!
        
        # Инициализация
        y_sp = {comp: 0.0 for comp in self.zi._composition.keys()}
        k_sp = None
        r_sp = None
        letuch_sp = None
        
        # БЛОК 2: ТОЧНО VBA
        if Sl > 1:
            if Sl > Sv:
                k_sp = phase_stability.k_values_liquid
                r_sp = phase_stability.ri_l
                letuch_sp = phase_stability.liquid_eos.fugacities
                y_sp = {comp: self.zi._composition[comp] / k_sp[comp]
                        for comp in self.zi._composition.keys()}
            else:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_sp = phase_stability.vapour_eos.fugacities
                y_sp = {comp: self.zi._composition[comp] * k_sp[comp]
                        for comp in self.zi._composition.keys()}
        else:
            if Sv < 1:
                y_sp = {comp: 0.0 for comp in self.zi._composition.keys()}
        
        # БЛОК 3: ТОЧНО VBA
        if Sv > 1:
            if Sv > Sl:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_sp = phase_stability.vapour_eos.fugacities
                y_sp = {comp: self.zi._composition[comp] * k_sp[comp]
                        for comp in self.zi._composition.keys()}
        else:
            if Sl < 1:
                y_sp = {comp: 0.0 for comp in self.zi._composition.keys()}
        
        # ТОЧНО VBA: Ssp = 0 + sum(ysp)
        S_sp = 0.0
        for comp in y_sp.keys():
            S_sp += y_sp[comp]
        
        return {'s_sp': S_sp, 'y_sp': y_sp, 'k_sp': k_sp, 'r_sp': r_sp,
                'letuch_sp': letuch_sp, 'letuch_z': letuch_z}  # ← ВСЕГДА letuch_z!

    def calculate_saturation_pressure(self, eos: EOS, max_iter=100):
        """Основной цикл - ТОЧНО VBA логика"""
        # Проверка на выход (аналог GoTo 59)
        if (self.p_max - self.p_min) < 1e-10:
            self.p_saturation = self.p_current
            return self.p_saturation
        
        iteration = 0
        while iteration < max_iter:
            # Получаем S_sp (аналог метки 347)
            result = self.define_s_sp(self.p_current, eos)
            S_sp = result['s_sp']
            
            # Метка 99: если Ssp = 0
            if abs(S_sp) < 1e-12:
                self.p_max = self.p_current
                self.p_current = (self.p_max + self.p_min) / 2
                iteration += 1
                continue  # GoTo 999
            
            # Сохраняем Rsp1 (НЕ используется, но точно как VBA)
            r_sp_old = result['r_sp'].copy() if result['r_sp'] else None
            
            # Пересчет Rsp (ТОЧНО VBA)
            r_sp = {}
            for comp in result['letuch_z'].keys():
                if result['letuch_sp'] is not None and result['s_sp'] > 0:
                    r_sp[comp] = math.exp(result['letuch_z'][comp]) / (
                        math.exp(result['letuch_sp'][comp]) * result['s_sp'])
                else:
                    r_sp[comp] = 1.0
            
            # lambda = 1 (ТОЧНО VBA, закомментированный Broyden отключен)
            lamb = 1.0
            
            # Пересчет ysp (ТОЧНО VBA)
            y_sp_new = {}
            for comp in result['y_sp'].keys():
                y_sp_new[comp] = result['y_sp'][comp] * (r_sp[comp] ** lamb)
            
            # Пересчет Ssp (ТОЧНО VBA)
            S_sp_new = 0.0
            for comp in y_sp_new.keys():
                S_sp_new += y_sp_new[comp]
            
            # Расчет критериев сходимости (ТОЧНО VBA)
            Ykz = 0.0
            Sum_log = 0.0
            for comp in self.zi._composition.keys():
                z_val = self.zi._composition[comp]
                y_val = y_sp_new[comp]
                if z_val != 0 and y_val != 0:
                    Ykz += y_val / z_val
                    Sum_log += math.log(r_sp[comp]) / math.log(y_val / z_val)
            
            # ТОЧНО VBA критерии: GoTo 100
            if abs(1 - S_sp_new) < 1e-3 or (Ykz ** 2) < 1e-4:
                self.p_saturation = self.p_current
                return self.p_saturation
            
            # ТОЧНО VBA: pmin = Pi: Pi = (pmax + pmin) / 2: GoTo 999
            self.p_min = self.p_current
            self.p_current = (self.p_max + self.p_min) / 2
            iteration += 1
            
            # Проверка на сходимость по давлению
            if (self.p_max - self.p_min) < 1e-10:
                self.p_saturation = self.p_current
                return self.p_saturation
        
        # Fallback если не сошлось
        self.p_saturation = self.p_current
        return self.p_saturation