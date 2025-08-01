from typing import Dict, Callable, Any
import math

class CriticalTemperatureCalculator:
    """Класс для расчета критической температуры, содержащий все корреляции"""
    
    @staticmethod
    def roess(gamma: float, t_bf: float) -> float:
        t_bf_fahrenheit = t_bf * 9/5 + 32
        t_c_renkin = 645.83 + 1.6667 * (gamma * (t_bf_fahrenheit + 100)) - \
                     (0.727e-3) * (gamma * (t_bf_fahrenheit + 100))**2
        return t_c_renkin * 5/9

    @staticmethod
    def nokey(gamma: float, t_b: float) -> float:
        return 19.07871 * t_b**0.58848 * gamma**0.2985 * 5/9

    @staticmethod
    def cavett(t_bf: float, gamma_api: float) -> float:
        return (768.07121 + 1.7133693 * t_bf - 0.10834003e-2 * t_bf**2 -
                0.89212579e-2 * t_bf * gamma_api +
                0.38890584e-6 * t_bf**3 + 
                0.5309492e-5 * t_bf**2 * gamma_api + 
                0.327116e-7 * t_bf**2 * gamma_api**2)

    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        """Возвращает функцию корреляции по имени"""
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)

    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        # Можно реализовать через аннотации функций или отдельный словарь
        params_map = {
            'roess': ['gamma', 't_bf'],
            'nokey': ['gamma', 't_b'],
            'cavett': ['t_bf', 'gamma_api']
        }
        return params_map.get(method, [])




class CriticalPressureCalculator:
    """Класс для расчета критического давления"""
    
    @staticmethod
    def kesler_lee(gamma: float, t_b: float) -> float:
        return 3.12281e9 / (t_b**2.3125 * gamma**2.3201)  # Пример

    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)




# Словарь для связи свойств с классами-калькуляторами
PROPERTY_CALCULATORS = {
    'critical_temperature': CriticalTemperatureCalculator,
    'critical_pressure': CriticalPressureCalculator,
    # Другие свойства...
}

class PlusComponentProperties:
    def __init__(self, component: str, correlations_config: Dict[str, str], data: Dict[str, Any]):
        self.component = component
        self.data = data
        self.correlations_config = correlations_config
    
    def calculate_property(self, property_name: str) -> float:
        """Универсальный метод расчета любого свойства"""
        if property_name not in PROPERTY_CALCULATORS:
            raise ValueError(f"Unknown property: {property_name}")
        
        method = self.correlations_config.get(property_name)
        if not method:
            raise ValueError(f"No correlation specified for {property_name}")
        
        calculator = PROPERTY_CALCULATORS[property_name]
        
        try:
            correlation_func = calculator.get_correlation(method.lower())
            required_params = calculator.get_required_params(method.lower())
        except ValueError as e:
            raise ValueError(f"Invalid correlation for {property_name}: {e}")
        
        # Подготовка параметров (можно добавить предварительную обработку)
        params = {}
        for param in required_params:
            if param == 'gamma_api' and 'gamma' in self.data:
                params[param] = 141.5/self.data['gamma'] - 131.5
            elif param in self.data:
                params[param] = self.data[param]
            else:
                raise ValueError(f"Missing required parameter '{param}' for {method}")
        
        return correlation_func(**params)

# Пример использования
if __name__ == '__main__':
    config = {
        'critical_temperature': 'Cavett',
        'critical_pressure': 'Kesler_Lee'
    }
    
    component_data = {
        'gamma': 0.8,
        't_bf': 300,
        't_b': 350,
        'molecular_weight': 100
    }
    
    calculator = PlusComponentProperties('C8', config, component_data)
    
    try:
        t_crit = calculator.calculate_property('critical_temperature')
        #p_crit = calculator.calculate_property('critical_pressure')
        print(f"Critical temperature: {t_crit:.2f} K")
        #print(f"Critical pressure: {p_crit:.2f} Pa")
    except ValueError as e:
        print(f"Error: {e}")