from typing import Dict, Callable, Any, List, Union
import math
import json

class CriticalTemperatureCorrelation:
    """Класс для расчета критической температуры, содержащий все корреляции"""
    
    @staticmethod
    def roess(gamma: float, Tb: float) -> float:
        t_bf_fahrenheit = Tb * 9/5 + 32
        t_c_renkin = 645.83 + 1.6667 * (gamma * (t_bf_fahrenheit + 100)) - \
                     (0.727e-3) * (gamma * (t_bf_fahrenheit + 100))**2
        return t_c_renkin * 5/9


    @staticmethod
    def nokey(gamma: float, Tb: float) -> float:
        return 19.07871 * Tb**0.58848 * gamma**0.2985 * 5/9


    @staticmethod
    def cavett(Tb: float, gamma_api: float) -> float:
        t_bf = Tb * 9/5 + 32
        return (768.07121 + 1.7133693 * t_bf - 0.10834003e-2 * t_bf**2 -
                0.89212579e-2 * t_bf * gamma_api +
                0.38890584e-6 * t_bf**3 + 
                0.5309492e-5 * t_bf**2 * gamma_api + 
                0.327116e-7 * t_bf**2 * gamma_api**2)


    @staticmethod
    def kesler_lee(gamma, Tb):
        t_c_renkin = 341.7 + 811 * gamma + (0.4244 + 0.1174 * gamma)*Tb + ((0.4669 - 3.2623 * gamma)* math.pow(10,5)) /(Tb)

        return t_c_renkin * 5/9


    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        """Возвращает функцию корреляции по имени"""
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)


    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        params_map = {
            'roess': ['gamma', 'Tb'],
            'nokey': ['gamma', 'Tb'],
            'cavett': ['Tb', 'gamma_api'],
            'kesler_lee': ['gamma', 'Tb']
        }
        return params_map.get(method, [])




class CriticalPressureCorrelation:
    """Класс для расчета критического давления"""
    
    @staticmethod
    def kesler_lee(gamma: float, Tb: float) -> float:
        return 3.12281e9 / (Tb**2.3125 * gamma**2.3201)  * 0.00689476


    @staticmethod
    def rizari_daubert(Tb, gamma):
        return (3.12281e9 * (Tb** -2.3125 * gamma**2.3201)) * 0.00689476

    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)


    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        params_map = {
            'kesler_lee': ['gamma', 'Tb'],
            'rizari_daubert' : ['gamma', 'Tb']
        }
        return params_map.get(method, [])




class AcentricFactorCorrelation:

    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        """Возвращает функцию корреляции по имени"""
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)


    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        params_map = {
            'edmister': ['p_c','t_c','Tb']
        }
        return params_map.get(method, [])
    
    @staticmethod
    def edmister(p_c, t_c, Tb) -> float:

        p_c = p_c * 145.038
        t_c = t_c * 1.8

        return (3/7) * (math.log10(p_c/14.7)/((t_c/Tb)-1)) - 1




class CriticalVolumeCorrelation:
    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        """Возвращает функцию корреляции по имени"""
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)


    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        params_map = {
            'rizari_daubert': ['Tb','gamma'],
            'hall_yarborough': ['M', 'gamma']
        }
        return params_map.get(method, [])
    

    @staticmethod
    def rizari_daubert(Tb, gamma):
        return (7.0434 * math.pow(10, -7)) * math.pow(Tb, 2.3829) * math.pow(gamma, -1.683)


    @staticmethod
    def hall_yarborough(M, gamma):
        return 0.025 * math.pow(M, 1.15) * math.pow(gamma, -0.7935)





class KWatson:

    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        """Возвращает функцию корреляции по имени"""
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)


    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        params_map = {
            'k_watson': ['Tb','gamma'],
            'k_watson_approx': ['M', 'gamma']
        }
        return params_map.get(method, [])
    

    @staticmethod
    def k_watson(Tb, gamma):
        return math.pow(Tb, 1/3) / gamma
    
    @staticmethod
    def k_watson_approx(M, gamma):
        return 4.5579 * math.pow(M, 0.15178) * math.pow(gamma, -0.84573)
    


class ShiftParameterCorrelation:
    @classmethod
    def get_correlation(cls, method: str) -> Callable:
        """Возвращает функцию корреляции по имени"""
        if not hasattr(cls, method):
            raise ValueError(f"Unknown correlation method: {method}")
        return getattr(cls, method)


    @classmethod
    def get_required_params(cls, method: str) -> list:
        """Возвращает список требуемых параметров для корреляции"""
        params_map = {
            'jhaveri_youngren': ['M', 'Kw']
        }
        return params_map.get(method, [])
    
    
    
    @staticmethod
    def jhaveri_youngren(M, Kw):
        
        #aromatic
        if 8.5 < Kw < 11:
            a0 = 2.516
            a1 = 0.2008

        #naften
        elif 11 < Kw < 12.5:
            a0 = 3.004
            a1 = 0.2324
        
        #parafin
        elif 12.5 < Kw < 13.5:
            a0 = 2.258
            a1 = 0.1823



        return 1 - (a0 / (math.pow(M, a1)))










class PlusComponentProperties:
    def __init__(self, component: str,  
                 correlations_config: Dict[str, str] ):
        self.component = component
        #self.data = data
        self.correlations_config = correlations_config
        

        self.property_classes = {
        'critical_temperature': CriticalTemperatureCorrelation,
        'critical_pressure': CriticalPressureCorrelation,
        'acentric_factor': AcentricFactorCorrelation,
        'critical_volume' : CriticalVolumeCorrelation,
        'k_watson' : KWatson,
        'shift_parameter': ShiftParameterCorrelation
        }

        
        with open('code/db/new_db.json') as f:
             self.katz_firuzabadi = json.load(f)

        self.data = {'M': self.katz_firuzabadi['molar_mass'][component], 'gamma': self.katz_firuzabadi['gamma'][component], 'Tb': self.katz_firuzabadi['Tb'][component]}
        
    


    def calculate_property(self, property_name: str) -> float:
        """Универсальный метод расчета любого свойства"""
        if property_name not in self.property_classes:
            raise ValueError(f"Unknown property: {property_name}")
        
        method = self.correlations_config.get(property_name)
        if not method:
            raise ValueError(f"No correlation specified for {property_name}")
        
        calculator = self.property_classes[property_name]
        
        try:
            correlation_func = calculator.get_correlation(method.lower())
            required_params = calculator.get_required_params(method.lower())
        except ValueError as e:
            raise ValueError(f"Invalid correlation for {property_name}: {e}")
        
        # Подготовка параметров
        params = {}
        for param in required_params:
            if param == 'gamma_api' and 'gamma_api' in self.data.keys():
                params[param] = 141.5/self.data['gamma'] - 131.5
            if param == 'Tb' and 'Tb' in self.data.keys():
                params[param] = self.data['Tb'] * 1.8
            # if param == 'p_c' and 'p_c' in self.data.keys():
            #     params[param] = self.data['p_c'] * 145.038
            # if param == 't_c' and 't_c' in self.data.keys():
            #     params[param] = self.data['t_c'] * 1.8
            elif param in self.data.keys():
                params[param] = self.data[param]
            else:
                raise ValueError(f"Missing required parameter '{param}' for {method}")
        
        return correlation_func(**params)
    


    def calculate_all_props_v2(self):


        self.data['p_c'] = self.calculate_property('critical_pressure')

        self.data['t_c'] = self.calculate_property('critical_temperature')

        self.data['acentric_factor'] = self.calculate_property('acentric_factor')

        self.data['crit_vol'] = self.calculate_property('critical_volume')

        self.data['Kw'] = self.calculate_property('k_watson')

        self.data['Cpen'] = self.calculate_property('shift_parameter')













    # def calculate_all_properties(self) -> Dict[str, Union[float, Dict[str, Any]]]:
    #     """
    #     Рассчитывает все свойства, указанные в correlations_config
        
    #     Возвращает словарь с результатами и дополнительной информацией:
    #     {
    #         'results': {property_name: value},
    #         'errors': {property_name: error_message},
    #         'used_correlations': correlations_config
    #     }
    #     """
    #     results = {}
    #     errors = {}
    #     self.component_data_with_calc = {}
        
    #     for property_name in self.correlations_config:
    #         try:
    #             results[property_name] = self.calculate_property(property_name)
    #         except ValueError as e:
    #             errors[property_name] = str(e)
        
    #     return {
    #         'results': results,
    #         'errors': errors,
    #         'used_correlations': self.correlations_config
    #     }




# Пример использования
if __name__ == '__main__':

    calculator = PlusComponentProperties('C7')
    
    calculator.calculate_all_props_v2()

    print(calculator.data)
    
