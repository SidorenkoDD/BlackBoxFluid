import json
import math as math

class PlusComponentAcentricFactor:
    ''' Класс для расчета ацентрического фактора +компонент

    В классе реализованы различные методы для расчета ацентрического фактора.

    Корреляции
    ----------
    * Kesler-Lee
    * 

    
    '''
    def __init__(self, method):
        pass

    @property
    def Kesler_Lee(self):
        return 5
    

class PlusComponentCriticalTemperature:
    '''Класс для расчета критической температуры + компонент

    В классе реализованы различные методы для расчета критической температуры компонента.

    Tcrit корреляции
    ----------
    * Roess
    * Nokey
    * Cavett
    * Kesler-Lee
    * Standing
    * Sim-Daubert
    * Rizari-Daubert
    * Pedersen
    * Twu - не реализовано
    * Watansiri - Owens - Starling - не реализовано
    * Mogoulas - Tassios - не реализовано
    '''

    def __init__(self):
        pass

    @property
    def Roess(self, gamma, t_bf):
        ##TODO: t_bf для корреляции должна быть в Фаренгейтах
        t_bf = t_bf 
        t_c_renkin = 645.83 + 1.6667 * (gamma *(t_bf + 100)) - (0.727 * math.pow(10, -3)) * math.pow((gamma *(t_bf + 100)),2)
        return t_c_renkin * 5/9


    @property
    def Nokey(self, gamma, t_b):
        ##TODO: в чем здесь дается Tb
        t_c_renkin = 19.07871 * math.pow(t_b, 0.58848) * math.pow(gamma, 0.2985)
        return t_c_renkin * 5/9
        
    
    @property
    def Cavett(self, t_bf, gamma):
        gamma_api = 141.5/gamma - 131.5
        t_c = (768.07121 + 1.7133693 * t_bf - 0.10834003 * math.pow(10, -2) * math.pow(t_bf, 2)
                - 0.89212579 * math.pow(10, -2) * t_bf * gamma_api +
                0.38890584 * math.pow(10, -6) * math.pow(t_bf, 3) + 
                0.5309492 * math.pow(10, -5)* math.pow(t_bf, 2) * gamma_api + 
                0.327116 * math.pow(10, -7)* math.pow(t_bf, 2) * math.pow(gamma_api,2))

        return t_c
    
    
    @property
    def Kelser_Lee(self, gamma, t_b):
        t_c = 341.7 + 811 * gamma + (0.4244 + 0.1174 * gamma)*t_b + ((0.4669 - 3.2623 * gamma)* math.pow(10,5)) /(t_b)

        return t_c
    

    @property
    def Standing(self, m, gamma):
        t_c = 338 + 202 * math.log10(m - 71.2) + (1361* math.log10(m) - 2111) * math.log10(gamma) 
        return t_c
    

    @property
    def Sim_Daubert(self, t_b, gamma):
        t_c = math.exp(3.9934718 * math.pow(t_b, 0.08615) * math.pow(gamma, 0.04614))
        return t_c
    

    @property
    def Rizari_Daubert(self, t_b, gamma):
        t_c = 24.27871 * math.pow(t_b,0.58848) * math.pow(gamma, 0.3596)
        return t_c
    

    @property
    def Pedersen(self, gamma, m):
        t_c = 163.12 * gamma + 86.052 * math.log(m) + 0.43475 * m - (1877.4/m)
        return t_c


    @property
    def Twu(self, t_b):
        ...






class PlusComponentCriticalPressure:
    '''Класс для расчета критической температуры + компонент

    В классе реализованы различные методы для расчета критической температуры компонента.

    Корреляции
    ----------
    * Cavett - не реализовано
    * Kesler-Lee - не реализовано
    '''

    def __init__(self):
        pass
    

    @property
    def Cavett(self):
        ...

class PlusComponentAcentricFactor:
    '''Класс для расчета ацентрического фактора + компонент

    В классе реализованы различные методы для расчета ацентрического фактора компонента.

    Корреляции
    ----------
    * Edmister - не реализовано
    * Kesler-Lee - не реализовано
    * Mogoulas-Tassios - не реализовано
    * Riazi-Al-Sahhaf - не реализовано
    '''
    def __init__(self):
        pass
    
    @property
    def Edmister(self):
        ...


class PlusComponentProperties:
    '''Класс для расчета свойств + компонент.
    Использует в себе классы: 
    * PlusComponentCriticalTemperature
    * PlusComponentCriticalPressure
    * PlusComponentAcentricFactor
    '''

    def __init__(self, acentric_factor_correlation):
        try:
            with open('code/db/katz_firuzabadi.json', 'r') as f:
                self.data = json.load(f)
                print(self.data)
        except FileNotFoundError:
            print("Файл не найден")
        except json.JSONDecodeError:
            print("Ошибка в формате JSON")


        self.critical_temperature = PlusComponentCriticalTemperature()
        self.critical_pressure = PlusComponentCriticalPressure()
        self.acentric_factor = PlusComponentAcentricFactor(acentric_factor_correlation)

        print(self.data)






if __name__ == '__main__':
    plus_comp_properties = PlusComponentProperties("Kesler_Lee")
    plus_comp_properties.critical_temperature