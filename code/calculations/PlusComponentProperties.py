import json

class PlusComponentAcentricFactor:
    def __init__(self, method):
        pass

    @property
    def Kesler_Lee(self):
        return 5
    

class PlusComponentCriticalTemperature:
    def __init__(self):
        pass

    @property
    def Roess(self):
        ...

    @property
    def Nokey(self):
        ...
    
    @property
    def Cavett(self):
        ...







class PlusComponentProperties:
    def __init__(self, acentric_factor_correlation):
        try:
            with open('code/db/katz_firuzabadi.json', 'r') as f:
                self.data = json.load(f)
                print(self.data)
        except FileNotFoundError:
            print("Файл не найден")
        except json.JSONDecodeError:
            print("Ошибка в формате JSON")


        self.acentric_factor = PlusComponentAcentricFactor(acentric_factor_correlation)

        print(self.data)


# class PlusComponentAcentricFactor:
#     def __init__(self):
#         pass



if __name__ == '__main__':
    plus_comp_properties = PlusComponentProperties("Kesler_Lee")
    plus_comp_properties.acentric_factor.Kesler_Lee