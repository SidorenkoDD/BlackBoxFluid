import math
import logging
import numpy as np
from calculations.PhaseStability.TwoPhaseStabilityTest import TwoPhaseStabilityTest
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition

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
        
        # Подготовка NumPy массивов для ускорения
        self.components = list(self.zi._composition.keys())
        self.n_components = len(self.components)
        self.z_array = np.array([self.zi._composition[comp] for comp in self.components], dtype=np.float64)
        
        # Кэш для последнего вызова
        self._last_p = None
        self._last_result = None
        
    def define_s_sp(self, p, eos: EOS):
        """Расчет S_sp с кэшированием"""
        
        if self._last_p is not None and abs(p - self._last_p) < 1e-10:
            return self._last_result
        
        phase_stability = TwoPhaseStabilityTest(self.zi, p, self.temp, eos)
        phase_stability.calculate_phase_stability()

        Sl = phase_stability.S_l
        Sv = phase_stability.S_v
        letuch_z = phase_stability.initial_eos.fugacities
        
        if (Sl - 1) < 1e-5 and (Sv - 1) < 1e-5:
            y_sp = {comp: 0.0 for comp in self.components}
            result = {'s_sp': 0.0, 'y_sp': y_sp, 'k_sp': None, 'r_sp': None,
                     'letuch_sp': None, 'letuch_z': letuch_z}
            self._last_p = p
            self._last_result = result
            return result
        
        y_sp_dict = {}
        
        if Sl > 1 and Sl > Sv:
            k_sp = phase_stability.k_values_liquid
            for comp in self.components:
                y_sp_dict[comp] = self.zi._composition[comp] / k_sp[comp]
        elif Sv > 1 and Sv > Sl:
            k_sp = phase_stability.k_values_vapour
            for comp in self.components:
                y_sp_dict[comp] = self.zi._composition[comp] * k_sp[comp]
        else:
            y_sp_dict = {comp: 0.0 for comp in self.components}
            k_sp = None
        
        S_sp = sum(y_sp_dict.values())
        
        result = {'s_sp': S_sp, 'y_sp': y_sp_dict, 'k_sp': k_sp, 'r_sp': None,
                'letuch_sp': None, 'letuch_z': letuch_z}
        
        self._last_p = p
        self._last_result = result
        return result
    
    def _get_residual(self, p, eos):
        """Получение невязки F(p) = S_sp - 1"""
        result = self.define_s_sp(p, eos)
        return result['s_sp'] - 1.0
    
    def calculate_saturation_pressure(self, eos: EOS, max_iter=60):
        """
        Гибридный метод: сначала бисекция для сужения интервала,
        затем метод секущих для быстрой финальной сходимости
        """
        
        # Проверка и расширение диапазона
        f_min = self._get_residual(self.p_min, eos)
        f_max = self._get_residual(self.p_max, eos)
        
        expansion_count = 0
        while f_min * f_max > 0 and expansion_count < 10:
            if f_min > 0 and f_max > 0:
                self.p_min = self.p_min / 2
                f_min = self._get_residual(self.p_min, eos)
                logger.info(f"Расширение p_min до {self.p_min:.3f}")
            elif f_min < 0 and f_max < 0:
                self.p_max = self.p_max * 2
                f_max = self._get_residual(self.p_max, eos)
                logger.info(f"Расширение p_max до {self.p_max:.3f}")
            else:
                break
            expansion_count += 1
        
        if f_min * f_max > 0:
            logger.error(f"Не удалось найти интервал! f(p_min)={f_min:.3e}, f(p_max)={f_max:.3e}")
            self.p_saturation = (self.p_min + self.p_max) / 2
            return self.p_saturation
        
        # ============= ЭТАП 1: БИСЕКЦИЯ ДЛЯ СУЖЕНИЯ =============
        logger.info(f"Этап 1: Бисекция для сужения интервала")
        
        p_low = self.p_min
        p_high = self.p_max
        f_low = f_min
        f_high = f_max
        
        # Сужаем интервал до тех пор, пока относительная ширина не станет < 10%
        # или не сделаем 15 итераций бисекции
        for bisect_iter in range(15):
            p_mid = (p_low + p_high) / 2
            f_mid = self._get_residual(p_mid, eos)
            
            logger.info(f"Бисекция {bisect_iter:2d} | P={p_mid:8.3f} | F={f_mid:10.3e} | dP={p_high-p_low:.3e}")
            
            if abs(f_mid) < 1e-7:
                self.p_saturation = p_mid
                logger.info(f"✅ Сходимость на бисекции: P_sat = {self.p_saturation:.3f} bar")
                return self.p_saturation
            
            if f_mid * f_low < 0:
                p_high = p_mid
                f_high = f_mid
            else:
                p_low = p_mid
                f_low = f_mid
            
            # Проверка ширины интервала
            relative_width = abs(p_high - p_low) / max(p_mid, 1.0)
            if relative_width < 0.01:  # Интервал сузился до 1%
                logger.info(f"Интервал сузился до {relative_width*100:.2f}%, переключение на метод секущих")
                break
        
        # ============= ЭТАП 2: МЕТОД СЕКУЩИХ ДЛЯ БЫСТРОЙ СХОДИМОСТИ =============
        logger.info(f"Этап 2: Метод секущих для быстрой финальной сходимости")
        
        p_prev = p_low
        p_curr = p_high
        f_prev = self._get_residual(p_prev, eos)
        f_curr = self._get_residual(p_curr, eos)
        
        for secant_iter in range(25):
            # Защита от деления на ноль
            if abs(f_curr - f_prev) < 1e-15:
                p_next = (p_curr + p_prev) / 2
            else:
                p_next = p_curr - f_curr * (p_curr - p_prev) / (f_curr - f_prev)
            
            # Ограничение интервалом
            p_next = max(p_low, min(p_high, p_next))
            
            f_next = self._get_residual(p_next, eos)
            
            logger.info(f"Секущие {secant_iter:2d} | P={p_next:8.3f} | F={f_next:10.3e} | dP={abs(p_next-p_curr):.3e}")
            
            # Проверка сходимости
            if abs(f_next) < 1e-5:
                self.p_saturation = p_next
                logger.info(f"✅ Сходимость методом секущих: P_sat = {self.p_saturation:.3f} bar")
                return self.p_saturation
            
            if abs(p_next - p_curr) < 1e-6:
                self.p_saturation = p_next
                logger.info(f"✅ Сходимость по давлению: P_sat = {self.p_saturation:.3f} bar")
                return self.p_saturation
            
            # Обновление
            p_prev, p_curr = p_curr, p_next
            f_prev, f_curr = f_curr, f_next
            
            # Если интервал слишком маленький - выходим
            if abs(p_high - p_low) < 1e-10:
                break
        
        # # ============= ФИНАЛЬНАЯ БИСЕКЦИЯ ДЛЯ ГАРАНТИИ =============
        # logger.info(f"Этап 3: Финальная бисекция для гарантии")
        
        # p_low = max(p_low, p_curr - abs(p_high - p_low))
        # p_high = min(p_high, p_curr + abs(p_high - p_low))
        
        # for final_iter in range(20):
        #     p_mid = (p_low + p_high) / 2
        #     f_mid = self._get_residual(p_mid, eos)
            
        #     if abs(f_mid) < 1e-5:
        #         self.p_saturation = p_mid
        #         logger.info(f"✅ Финальная сходимость: P_sat = {self.p_saturation:.3f} bar")
        #         return self.p_saturation
            
        #     if f_mid * self._get_residual(p_low, eos) < 0:
        #         p_high = p_mid
        #     else:
        #         p_low = p_mid
            
        #     if (p_high - p_low) < 1e-10:
        #         self.p_saturation = p_mid
        #         break
        
        self.p_saturation = (p_low + p_high) / 2
        logger.info(f"✅ P_sat = {self.p_saturation:.3f} bar")
        return self.p_saturation
    
    def clear_cache(self):
        """Очистка кэша"""
        self._last_p = None
        self._last_result = None