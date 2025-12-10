import math
from typing import Dict, Callable
from calculations.Utils.JsonDBReader import JsonDBReader
from calculations.Utils.Constants import CONSTANT_R
import sys
from pathlib import Path
# Добавляем корневую директорию в PYTHONPATH 
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

class CriticalTemperatureCorrelation:
    """Класс для расчета критической температуры, содержащий все корреляции"""

    @staticmethod
    def roess(gamma: float, Tb: float) -> float:
        t_bf_fahrenheit = Tb * 9/5 + 32
        t_c_renkin = (645.83 + 1.6667 * (gamma * (t_bf_fahrenheit + 100)) -
                     (0.727e-3) * (gamma * (t_bf_fahrenheit + 100))**2)
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
        t_c_renkin = (341.7 + 811 * gamma + (0.4244 + 0.1174 * gamma) * 
                      Tb + ((0.4669 - 3.2623 * gamma)* math.pow(10,5)) /(Tb))
        return t_c_renkin * 5/9

    @staticmethod
    def pedersen(gamma, M):
        return 163.12 * gamma + 86.052 * math.log(M) + 0.43475 * M - (1877.4/M)

    @staticmethod
    def standing(gamma, M):
        return 338 + 202 * math.log10(M - 71.2) + (1361 * math.log10(M) - 2111) * math.log10(gamma)

    @staticmethod
    def sim_daubert(gamma, Tb):
        return math.exp(3.9934718 * math.pow(Tb, 0.08615) * math.pow(gamma, 0.04614))

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
            'kesler_lee': ['gamma', 'Tb'],
            'pedersen' : ['gamma', 'M'],
            'standing' : ['gamma', 'M'],
            'sim_daubert': ['gamma', 'Tb'],
        }
        return params_map.get(method, [])

class CriticalPressureCorrelation:
    """Класс для расчета критического давления"""

    @staticmethod
    def kesler_lee(gamma: float, Tb: float) -> float:
        first = 8.3634 - (0.0566 / gamma)
        second = - ((0.24244 + (2.2898 / gamma) + (0.11857 / math.pow(gamma, 2))) * math.pow(10, -3) * Tb)
        third = ((1.4685 + (3.648 / gamma) + (0.47227 / math.pow(gamma, 2))) * math.pow(10, -7) * math.pow(Tb, 2))
        fourth = - ((0.42019 + (1.6977/math.pow(gamma, 2))) * math.pow(10, -10)* math.pow(Tb, 3))
        return math.pow(math.e, sum([first, second, third, fourth])) * 0.00689476

    @staticmethod
    def rizari_daubert(Tb, gamma):
        return (3.12281e9 * (Tb** -2.3125 * gamma**2.3201)) * 0.00689476

    @staticmethod
    def pedersen(gamma, M):
        return (math.exp(-0.13408 + 2.5019 * gamma + (208.46/M) - (3987.2/ math.pow(M,2)))) / 10

    @staticmethod
    def standing(gamma, M):
        return (8.191 - 2.97 * math.log10(M - 61.1) + (15.99 - 5.87 *
                                                        math.log10(M - 53.7)) * (gamma - 0.8))

    @staticmethod
    def sim_daubert(gamma, Tb):
        return 3.48242 * math.pow(10, 9) * math.pow(Tb, -2.3177) * math.pow(gamma, 2.4853) * 0.00689476

    @staticmethod
    def pc_from_eos(gamma, M, Tc):

        def calc_a(omega_a = 0.45724) -> float:
            '''Caclulation of **a** parameter for EOS

            Parameters:
                ---------
                    component - component for calculation parameter a
                    omega_a - constant 0.45724

            Returns:
                --------
                    parameter **a** for component
            '''
            acentric_factor =  - (0.3 - math.exp(-6.252 + 3.64457 * math.pow(M, 0.1)))
            print(acentric_factor)
            if acentric_factor > 0.49:
                m = (0.3796 + 1.485 * acentric_factor  - 
                    0.1644 * math.pow(acentric_factor,2) + 
                    0.01667 * math.pow(acentric_factor, 3))
            else:
                m = (0.37464 + 1.54226 * acentric_factor - 
                    0.26992 * math.pow(acentric_factor, 2))

            alpha = math.pow(1 + m * (1 - math.sqrt(293.14/Tc)), 2)
            
            return (omega_a * math.pow(Tc,2) * 
                    math.pow(8.31, 2) * alpha)

        p_std = 101325 # Pa
        t_std = 293.14 # K
        molar_mass_kg_mole = M / 1000
        molar_volume = (molar_mass_kg_mole) / (gamma * math.pow(10,3))
        a = calc_a(Tc)
        b = 0.0778 * CONSTANT_R * Tc

        bk = ((p_std * b * molar_volume - (2 * CONSTANT_R * t_std * b) + a) /
               (p_std * math.pow(molar_volume, 2) - (CONSTANT_R * t_std * molar_volume)))
        
        ck =  (((3 * p_std * math.pow(b,2) * molar_volume) + 
                (math.pow(b, 2) * CONSTANT_R * t_std) - (a * b)) /
               ((p_std * math.pow(molar_volume, 3)) - (CONSTANT_R * t_std * math.pow(molar_volume, 2))))
        dk = (p_std * math.pow(b,3) / 
              ((p_std * math.pow(molar_volume, 3)) - (CONSTANT_R * t_std * math.pow(molar_volume, 2))))
        pk = -(bk ** 2) / 3 + ck
        qk = 2 * (bk ** 3) / 27 - (bk * ck/ 3 ) + dk
        s = ((pk/3) ** 3) + ((qk/2) ** 2) 

        if s > 0:
            vb = -qk/2 - (s ** (1/2)) 
            itt = -qk/2 + (s ** (1/2)) 
            if itt < 0:

                itt =  abs(itt)

                it =  (itt ** (1/3))
                it = - (itt ** (1/3))
            else:
                 it = itt ** (1/3)
            if vb < 0:
                    zk0 = it - ((abs(vb)) ** (1/3)) - bk/3
            else:
                    zk0 = it + ((-qk/2 - math.sqrt(s)) ** (1/3)) - bk/3
            zk1 = 0
            zk2 = 0
        elif s < 0:
            if qk < 0:
                f = math.atan(math.sqrt(-s) / (-qk/2))
            elif qk > 0:
                f = math.atan(math.sqrt(-s) / (-qk/2)) + math.pi
            else:
                f = math.pi / 2

            zk0 = 2 * math.sqrt(-pk/3) * math.cos(f/3) - bk/3
            zk1 = 2 * math.sqrt(-pk/3) * math.cos(f/3 + 2 * math.pi /3) - bk/3 
            zk2 = 2 * math.sqrt(-pk/3) * math.cos(f/3 + 4 * math.pi /3) - bk/3
        
        elif s == 0:
            zk0 = 2 * math.sqrt(-qk / 2) - bk/3
            zk1 = -math.pow((-qk/2), (1/3)) - bk/3
            zk2 = -math.pow((-qk/2), (1/3)) - bk/3


        return [zk0, zk1, zk2]

    @staticmethod
    def mogoulas_tassios(gamma, M):
        return math.pow(math.e,(0.01901 - 0.0048442 * M + 0.13239 * gamma + (227/M) - (1.1663/gamma) + 1.2702 * math.log(M))) * 0.00689476

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
            'rizari_daubert' : ['gamma', 'Tb'],
            'pedersen' : ['gamma', 'M'], 
            'standing' : ['gamma', 'M'],
            'pc_from_eos' : ['gamma', 'M', 'Tc'],
            'sim_daubert' : ['gamma', 'Tb'],
            'mogoulas_tassios' : ['gamma', 'M']
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
            'edmister': ['p_c','t_c','Tb'],
            'rizari_al_sahhaf' : ['M']
        }
        return params_map.get(method, [])
    
    @staticmethod
    def edmister(p_c, t_c, Tb) -> float:

        p_c = p_c * 145.038
        t_c = t_c * 1.8

        return (3/7) * (math.log10(p_c/14.7)/((t_c/Tb)-1)) - 1


    @staticmethod
    def rizari_al_sahhaf(M):
        return - (0.3 - math.exp(-6.252 + 3.64457 * math.pow(M, 0.1)))

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
            'hall_yarborough': ['M', 'gamma'],
            'crit_vol_from_eos' : ['acentric_factor', 'Pc', 'Tc'],
            'pedersen_supposed' : ['M', 'gamma']
        }
        return params_map.get(method, [])
    

    @staticmethod
    def rizari_daubert(Tb, gamma):
        return (7.0434 * math.pow(10, -7)) * math.pow(Tb, 2.3829) * math.pow(gamma, -1.683)


    @staticmethod
    def hall_yarborough(M, gamma):
        return 0.025 * math.pow(M, 1.15) * math.pow(gamma, -0.7935)


    @staticmethod
    def crit_vol_from_eos(acentric_factor, Pc, Tc):
        return (0.2918 - 0.0928 * acentric_factor) * CONSTANT_R * Tc / Pc

    @staticmethod
    def pedersen_supposed(M, gamma):
        return 21.573 + 0.015122 *  M - 27.656 * gamma + 0.070615 * M * gamma


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
            'jhaveri_youngren': ['M', 'Kw'],
            'pedersen' : ['acentric_factor', 'p_c', 't_c']
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

    @staticmethod
    def pedersen(acentric_factor, p_c, t_c):
        z_ra = 0.29056 - 0.08775 * acentric_factor
        return 0.40768 * (CONSTANT_R * t_c / (p_c)) * (0.29441 - z_ra)

class PlusComponentProperties:
    '''Main class to calculate all properties.
    '''
    def __init__(self, component: str,  
                 correlations_config: Dict[str, str] ):
        self.component = component

        self.correlations_config = correlations_config
        

        self.property_classes = {
        'critical_temperature': CriticalTemperatureCorrelation,
        'critical_pressure': CriticalPressureCorrelation,
        'acentric_factor': AcentricFactorCorrelation,
        'critical_volume' : CriticalVolumeCorrelation,
        'k_watson' : KWatson,
        'shift_parameter': ShiftParameterCorrelation
        }

        jsondbreader = JsonDBReader()
        self.katz_firuzabadi = jsondbreader.load_database()


        self.data = {'M': self.katz_firuzabadi['molar_mass'][component],
                    'gamma': self.katz_firuzabadi['gamma'][component],
                    'Tb': self.katz_firuzabadi['Tb'][component]}
        
    


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



# Пример использования
if __name__ == '__main__':

    calculator = PlusComponentProperties('C7')
    
    calculator.calculate_all_props_v2()

    print(calculator.data)
    
