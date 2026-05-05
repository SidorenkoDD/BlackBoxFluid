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
        """
        Инициализация расчета давления насыщения с NumPy векторизацией
        
        Args:
            composition_object: Объект состава
            p_max: Максимальное давление поиска (bar)
            temp: Температура (Celsius)
            p_min: Минимальное давление поиска (bar)
        """
        self.zi = composition_object
        self.p_min = p_min
        self.p_max = p_max
        self.p_current = (p_max + p_min) / 2
        self.temp = temp + 273.14
        self.results = {}
        
        # Векторизация через NumPy
        self.components = list(self.zi._composition.keys())
        self.n_components = len(self.components)
        
        # NumPy массивы мольных долей
        self.z_array = np.array([self.zi._composition[comp] for comp in self.components], dtype=np.float64)
        
        # Маска для ненулевых компонентов (для ускорения операций)
        self.nonzero_mask = self.z_array > 1e-15
        
        # Словарь для быстрого доступа по имени (сохраняем для совместимости)
        self.z_dict = self.zi._composition.copy()
        
        # Кэш результатов стабильности для близких давлений
        self.stability_cache = {}
        self.cache_maxsize = 8
        self.cache_tolerance = 1e-6
        
        # Предварительное выделение рабочих массивов
        self._y_sp_work = np.zeros(self.n_components, dtype=np.float64)
        self._r_sp_work = np.ones(self.n_components, dtype=np.float64)
        self._letuch_z_array = np.zeros(self.n_components, dtype=np.float64)
        self._letuch_sp_array = np.zeros(self.n_components, dtype=np.float64)
        
    def _get_cache_key(self, p):
        """Создание ключа для кэша с округлением"""
        return round(p, 6)
    
    def _update_cache(self, key, p, result):
        """Обновление кэша с ограничением размера"""
        if len(self.stability_cache) >= self.cache_maxsize:
            # Удаляем самый старый элемент
            oldest_key = next(iter(self.stability_cache))
            del self.stability_cache[oldest_key]
        self.stability_cache[key] = {'p': p, 'result': result}
    
    def _dict_to_array(self, fugacities_dict):
        """Быстрая конвертация словаря фугитивностей в numpy массив"""
        if fugacities_dict is None:
            return None
        return np.array([fugacities_dict[comp] for comp in self.components], dtype=np.float64)
    
    def _array_to_dict(self, array, name_prefix=''):
        """Конвертация numpy массива в словарь (для совместимости)"""
        if array is None:
            return None
        return {self.components[i]: array[i] for i in range(self.n_components)}
    
    def define_s_sp(self, p, eos: EOS):
        """
        Определение S_sp и состава паровой фазы с NumPy векторизацией
        
        Args:
            p: Давление (bar)
            eos: Объект уравнения состояния
            
        Returns:
            dict: Результаты расчета
        """
        # Проверка кэша
        cache_key = self._get_cache_key(p)
        if cache_key in self.stability_cache:
            cached = self.stability_cache[cache_key]
            if abs(cached['p'] - p) < self.cache_tolerance:
                return cached['result']
        
        # Вызов теста стабильности
        phase_stability = TwoPhaseStabilityTest(self.zi, p, self.temp, eos)
        phase_stability.calculate_phase_stability()
        
        Sl = phase_stability.S_l
        Sv = phase_stability.S_v
        letuch_z = phase_stability.initial_eos.fugacities
        
        # БЛОК 1: Если обе фазы стабильны
        if (Sl - 1) < 1e-5 and (Sv - 1) < 1e-5:
            y_sp = {comp: 0.0 for comp in self.components}
            result = {
                's_sp': 0.0,
                'y_sp': y_sp,
                'k_sp': None,
                'r_sp': None,
                'letuch_sp': None,
                'letuch_z': letuch_z,
                # NumPy массивы для внутреннего использования
                '_y_sp_array': np.zeros(self.n_components),
                '_letuch_z_array': self._dict_to_array(letuch_z),
                '_letuch_sp_array': None
            }
            self._update_cache(cache_key, p, result)
            return result
        
        # Инициализация
        y_sp_array = np.zeros(self.n_components)
        k_sp = None
        r_sp = None
        letuch_sp = None
        letuch_sp_array = None
        
        # БЛОК 2: Обработка жидкой фазы
        if Sl > 1:
            if Sl > Sv:
                # Используем liquid K-values
                k_sp = phase_stability.k_values_liquid
                r_sp = phase_stability.ri_l
                letuch_sp = phase_stability.liquid_eos.fugacities
                # Векторизованный расчет y_i = z_i / K_i
                k_array = np.array([k_sp[comp] for comp in self.components])
                # Защита от деления на ноль
                k_array_safe = np.where(np.abs(k_array) < 1e-12, 1e-12, k_array)
                y_sp_array = self.z_array / k_array_safe
            else:
                # Используем vapour K-values
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_sp = phase_stability.vapour_eos.fugacities
                # Векторизованный расчет y_i = z_i * K_i
                k_array = np.array([k_sp[comp] for comp in self.components])
                y_sp_array = self.z_array * k_array
        
        # БЛОК 3: Обработка паровой фазы
        if Sv > 1:
            if Sv > Sl:
                k_sp = phase_stability.k_values_vapour
                r_sp = phase_stability.ri_v
                letuch_sp = phase_stability.vapour_eos.fugacities
                # Векторизованный расчет y_i = z_i * K_i
                k_array = np.array([k_sp[comp] for comp in self.components])
                y_sp_array = self.z_array * k_array
        elif Sl < 1:
            # Обнуляем массив
            y_sp_array = np.zeros(self.n_components)
        
        # Конвертация массивов для результата
        letuch_z_array = self._dict_to_array(letuch_z)
        if letuch_sp is not None:
            letuch_sp_array = self._dict_to_array(letuch_sp)
        
        # Расчет S_sp (сумма y_sp)
        S_sp = float(np.sum(y_sp_array))
        
        # Конвертация в словарь для совместимости с внешним кодом
        y_sp_dict = {self.components[i]: y_sp_array[i] for i in range(self.n_components)}
        
        result = {
            's_sp': S_sp,
            'y_sp': y_sp_dict,
            'k_sp': k_sp,
            'r_sp': r_sp,
            'letuch_sp': letuch_sp,
            'letuch_z': letuch_z,
            # NumPy массивы для внутреннего использования (ускоряет последующие итерации)
            '_y_sp_array': y_sp_array,
            '_letuch_z_array': letuch_z_array,
            '_letuch_sp_array': letuch_sp_array
        }
        
        self._update_cache(cache_key, p, result)
        return result
    
    def calculate_saturation_pressure(self, eos: EOS, max_iter=500):
        """
        Расчет давления насыщения (bubble point) с NumPy векторизацией
        
        Args:
            eos: Объект уравнения состояния
            max_iter: Максимальное количество итераций
            
        Returns:
            float: Давление насыщения (bar)
        """
        iteration = 0
        
        # Локальные переменные для скорости доступа
        z_array = self.z_array
        nonzero_mask = self.nonzero_mask
        
        # Основной цикл
        while iteration < max_iter:
            # Вызов теста стабильности
            result = self.define_s_sp(self.p_current, eos)
            S_sp = result['s_sp']
            
            # Быстрая проверка на ноль
            if abs(S_sp) < 1e-12:
                self.p_max = self.p_current
                self.p_current = (self.p_max + self.p_min) * 0.5
                iteration += 1
                continue
            
            # Получение NumPy массивов из результата
            y_sp_array = result.get('_y_sp_array')
            letuch_z_array = result.get('_letuch_z_array')
            letuch_sp_array = result.get('_letuch_sp_array')
            
            # Если массивов нет, создаем их из словарей
            if y_sp_array is None:
                y_sp_array = np.array([result['y_sp'][comp] for comp in self.components])
            
            # Пересчет Rsp векторизованно
            S_safe = max(S_sp, 1e-8)
            
            if letuch_sp_array is not None and letuch_z_array is not None and S_sp > 1e-6:
                # Векторизованный расчет Rsp для всех компонентов
                # Защита от переполнения
                exp_z = np.exp(np.clip(letuch_z_array, -700, 700))
                exp_sp = np.exp(np.clip(letuch_sp_array, -700, 700))
                r_sp_array = exp_z / (exp_sp * S_safe)
                # Замена inf и nan на 1.0
                r_sp_array = np.where(np.isfinite(r_sp_array), r_sp_array, 1.0)
            else:
                r_sp_array = np.ones(self.n_components)
            
            # Затухание для летучих смесей
            lamb = 0.85 if iteration > 30 else 1.0
            
            # Векторизованный пересчет y_sp
            if lamb == 1.0:
                # Быстрый путь без затухания
                y_sp_new_array = y_sp_array * r_sp_array
            else:
                # С затуханием
                y_sp_new_array = y_sp_array * (r_sp_array ** lamb)
            
            # Расчет S_sp_new
            S_sp_new = float(np.sum(y_sp_new_array))
            
            # Векторизованный расчет Ykz
            # Используем маску для ненулевых компонентов
            y_nonzero = y_sp_new_array[nonzero_mask]
            z_nonzero = z_array[nonzero_mask]
            Ykz = float(np.sum(y_nonzero / np.maximum(z_nonzero, 1e-15)))
            
            # Логирование (каждые 3 итерации для уменьшения вывода)
            if iteration % 3 == 0 or iteration < 10 or abs(1.0 - S_sp_new) < 1e-2:
                logger.info(f"Iter {iteration:3d} | P={self.p_current:8.3f} | S_sp={S_sp_new:10.6e} | Ykz={Ykz:8.4f}")
            
            # Критерий сходимости по S_sp
            if iteration >= 5:
                if abs(1.0 - S_sp_new) < 1e-3:
                    if Ykz < 2.0:
                        self.p_saturation = self.p_current
                        logger.info(f"✅ Сходимость достигнута. P_sat = {self.p_saturation:.3f} bar")
                        return self.p_saturation
            
            # Fallback критерий по Ykz
            if iteration >= 5 and (Ykz * Ykz) < 1e-4:
                self.p_saturation = self.p_current
                logger.info(f"✅ Сходимость по Ykz. P_sat = {self.p_saturation:.3f} bar")
                return self.p_saturation
            
            # Бисекция
            p_prev = self.p_current
            if S_sp_new > 1.0:
                self.p_min = self.p_current
            else:
                self.p_max = self.p_current
            
            self.p_current = (self.p_max + self.p_min) * 0.5
            
            # Защита от зацикливания
            if abs(self.p_current - p_prev) < 1e-12:
                step = 1e-6 * max(1.0, self.p_current)
                if S_sp_new > 1.0:
                    self.p_current = p_prev + step
                    self.p_max = self.p_current
                else:
                    self.p_current = p_prev - step
                    self.p_min = self.p_current
            
            iteration += 1
            
            # Проверка сходимости интервала
            if (self.p_max - self.p_min) < 1e-10:
                logger.warning(f"⚠️ Интервал давления исчерпан. P_sat ≈ {self.p_current:.3f} bar")
                break
        
        self.p_saturation = self.p_current
        logger.warning(f"⚠️ Завершение по лимиту итераций ({max_iter}). P_sat ≈ {self.p_saturation:.3f} bar")
        return self.p_saturation
    
    def clear_cache(self):
        """Очистка кэша стабильности"""
        self.stability_cache.clear()
    
    def get_statistics(self):
        """Получение статистики использования"""
        return {
            'cache_size': len(self.stability_cache),
            'n_components': self.n_components,
            'components': self.components,
            'nonzero_components': int(np.sum(self.nonzero_mask)),
            'z_sum': float(np.sum(self.z_array))
        }
    
    def set_initial_pressure(self, p_initial):
        """Установка начального давления для ускорения сходимости"""
        if self.p_min < p_initial < self.p_max:
            self.p_current = p_initial
            logger.info(f"Установлено начальное давление: {p_initial:.3f} bar")
        else:
            logger.warning(f"Начальное давление {p_initial:.3f} вне диапазона [{self.p_min:.3f}, {self.p_max:.3f}]")