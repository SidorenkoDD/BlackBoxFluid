import math



class BIPsCalculation:
    def __init__(self):
        pass
    
    def _chueh_prausnitz_bip(self, component_i, component_j, A = 0.18, B = 6):

        v_ci = self.composition_data['critical_volume'][component_i]
        v_cj = self.composition_data['critical_volume'][component_j]

        return A * (1 - math.pow(((2 * math.pow(v_ci, 1/6) * math.pow(v_cj, 1/6))/(math.pow(v_ci, 1/3) + math.pow(v_cj, 1/3))), B))

