import yaml
import math as math

class EOS_PR:
    def __init__(self, zi:dict, p, t):
        # Читаем .yaml файл с данными по компонентам
        with open('code/db.yaml', 'r') as db_file:
            self.db = yaml.safe_load(db_file)
        print(self.db['critical_temperature']['C1'])
        # компонентный состав
        self.zi = zi

        # Давление для расчета
        self.p = p

        # температура для расчета
        self.t = t

        # параметры а и b, рассчитанные для всего заданного компонентного состава
        self.all_params_a = []
        self.all_params_b = []
        for key in self.zi.keys():
            self.all_params_a.append(self.calc_a(component=key))
            self.all_params_b.append(self.calc_b(component=key))

        # Параметры А и В, рассчитанные для всего компонентного состава
        self.all_params_A = []
        self.all_params_B = []

        for key in self.zi.keys():
            self.all_params_A.append(self.calc_A(component=key))
            self.all_params_B.append(self.calc_B(component=key))

    
    def calc_a(self, component, omega_a = 0.45724):
        if self.db['acentric_factor'][component] > 0.49:
            m = 0.3796 + 1.485 * self.db['acentric_factor'][component]  - 0.1644 * math.pow(self.db['acentric_factor'][component],2) + 0.01667 * math.pow(self.db['acentric_factor'][component], 3)
        else:
            m = 0.37464 + 1.54226 * self.db['acentric_factor'][component] - 0.26992 * math.pow(self.db['acentric_factor'][component], 2)

        alpha = math.pow(1 + m * (1 - math.sqrt(self.t/self.db['critical_temperature'][component])), 2)
        return omega_a * math.pow(self.db['critical_temperature'][component],2) * math.pow(8.314,2) * alpha / self.db['critical_pressure'][component]

    
    def calc_b(self, component, omega_b = 0.0778):
        return omega_b * 8.314 * self.db['critical_temperature'][component] / self.db['critical_pressure'][component]
    

    def calc_A(self, component):
        return self.calc_a(component) * self.p/math.pow((8.314 * self.t), 2)
    
    def calc_B(self, component):
        return self.calc_b(component) * self.p/ (8.314 * self.t)


if __name__ == '__main__':
    eos = EOS_PR({'C2': 100}, 100, 100)
    print(eos.all_params_a)
    print(eos.all_params_b)
    print(eos.all_params_A)
    print(eos.all_params_B)