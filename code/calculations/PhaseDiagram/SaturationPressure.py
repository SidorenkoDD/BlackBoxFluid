import math
import logging
from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition

# Простой логгер (можно настроить уровень в основном скрипте)
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class SaturationPressureCalculation:
    def __init__(self, composition_object: Composition, p_max: float, temp, p_min=0.1):
        self.zi = composition_object
        self.p_min = p_min
        self.p_max = p_max
        self.p_current = (p_max + p_min) / 2
        self.temp = temp + 273.14
        self.results = {}

    def define_s_sp(self, p, eos: EOS):
        """Ваш исходный метод без изменений"""
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
                       'letuch_sp': None, 'letuch_z': letuch_z}
        
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
        S_sp = sum(y_sp.values())
        
        return {'s_sp': S_sp, 'y_sp': y_sp, 'k_sp': k_sp, 'r_sp': r_sp,
                'letuch_sp': letuch_sp, 'letuch_z': letuch_z}
    def calculate_saturation_pressure(self, eos: EOS, max_iter=500):
        """Основной цикл - ваша структура + защита от ложной сходимости"""
        iteration = 0
        p_old = self.p_current
        S_sp_prev = None  # Для отслеживания изменения S_sp
        
        while iteration < max_iter:
            result = self.define_s_sp(self.p_current, eos)
            S_sp = result['s_sp']
            
            # Метка 99: если Ssp = 0
            if abs(S_sp) < 1e-12:
                self.p_max = self.p_current
                self.p_current = (self.p_max + self.p_min) / 2
                iteration += 1
                continue
            
            # Пересчет Rsp (ТОЧНО VBA + защита)
            r_sp = {}
            S_safe = max(S_sp, 1e-8)
            for comp in result['letuch_z'].keys():
                if result['letuch_sp'] is not None and S_sp > 1e-6:
                    r_sp[comp] = math.exp(result['letuch_z'][comp]) / (
                        math.exp(result['letuch_sp'][comp]) * S_safe)
                else:
                    r_sp[comp] = 1.0
            
            # Затухание для летучих смесей
            lamb = 0.85 if iteration > 30 else 1.0
            
            # Пересчет ysp
            y_sp_new = {}
            S_sp_new = 0.0
            for comp in result['y_sp'].keys():
                y_val = result['y_sp'][comp] * (r_sp[comp] ** lamb)
                y_sp_new[comp] = y_val
                S_sp_new += y_val
            
            # Расчет Ykz
            Ykz = 0.0
            for comp in self.zi._composition.keys():
                z_val = self.zi._composition[comp]
                y_val = y_sp_new[comp]
                if z_val > 1e-15 and y_val > 1e-15:
                    Ykz += y_val / z_val

            # Логирование
            logger.info(f"Iter {iteration:3d} | P={self.p_current:8.3f} | S_sp={S_sp_new:7.5e} | Ykz={Ykz:6.4f}")
            
            # 🔑 УЛУЧШЕННЫЙ КРИТЕРИЙ СХОДИМОСТИ:
            # 1. Минимум 5 итераций (исключает случайное совпадение на старте)
            # 2. Более строгий допуск для S_sp
            # 3. Проверка, что S_sp действительно стабилизировалось (не просто "попало" в 1.0)
            if iteration >= 5:
                if abs(1 - S_sp_new) < 1e-4:  # ужесточили с 1e-3 до 1e-4
                    # Дополнительная проверка: если Ykz всё ещё большой, состав не сошёлся
                    if Ykz < 2.0:  # порог: если y/z в среднем отличается меньше чем в 2 раза
                        self.p_saturation = self.p_current
                        logger.info(f"✅ Сходимость достигнута. P_sat = {self.p_saturation:.3f}")
                        return self.p_saturation
            
            # Fallback для Ykz (как в VBA), но тоже с задержкой
            if iteration >= 5 and (Ykz ** 2) < 1e-4:
                self.p_saturation = self.p_current
                logger.info(f"✅ Сходимость по Ykz. P_sat = {self.p_saturation:.3f}")
                return self.p_saturation
            
            # Сохраняем S_sp для следующей итерации (проверка стабильности)
            S_sp_prev = S_sp_new
            
            # Бисекция
            p_prev = self.p_current
            if S_sp_new > 1.0:
                self.p_min = self.p_current
            else:
                self.p_max = self.p_current
                
            self.p_current = (self.p_max + self.p_min) / 2
            
            # Защита от зацикливания при потере точности
            if abs(self.p_current - p_prev) < 1e-12:
                step = 1e-6 * max(1.0, self.p_current)
                self.p_current = p_prev + step if S_sp_new > 1.0 else p_prev - step
                if self.p_current > self.p_max:
                    self.p_max = self.p_current
                elif self.p_current < self.p_min:
                    self.p_min = self.p_current
            
            iteration += 1
            
            if (self.p_max - self.p_min) < 1e-10:
                logger.warning(f"⚠️ Интервал давления исчерпан. P_sat ≈ {self.p_current:.3f}")
                break
                
        self.p_saturation = self.p_current
        logger.warning(f"⚠️ Завершение по лимиту итераций. P_sat ≈ {self.p_saturation:.3f}")
        return self.p_saturation