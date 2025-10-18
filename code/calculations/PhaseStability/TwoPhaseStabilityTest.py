from pathlib import Path
import sys
import math as math
from calculations.PhaseStability.BasePhaseStability import PhaseStabilityTest
from calculations.EOS.BaseEOS import EOS
from calculations.EOS.RootChooser import EOSRootChooser
from calculations.EOS.EOSFactory import EOSFactory
from code.calculations.Utils.Constants import TOL_TWO_PHASE_STABILITY_CONVERGENCE, TOL_TWO_PHASE_STABILITY_CONVERGENCE_TRIVIAL_SOLUTION

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))


class TwoPhaseStabilityTest(PhaseStabilityTest):
     
    def __init__(self, composition, p, t, eos:EOS):
        super().__init__(composition, p, t, eos)

        self.convergence = False
        self.convergence_trivial_solution = False
        self.eos = EOSFactory.create_eos(eos)

        self.composition = composition._composition
        self.composition_data = composition._composition_data
    
    # Расчет начального УРС
    def calc_initial_eos(self):
        initial_eos = self.eos(zi = self.composition, components_properties=self.composition_data, p = self.p, t = self.t)
        initial_eos.calc_eos()
        return initial_eos

    # Расчет начальных констант равновесия для газовой фазы
    def calc_k_initial_for_vapour_wilson(self):
        k_initial_vapour = {}
        for component in list(self.composition.keys()):
            k_initial_vapour[component] = (math.pow(math.e, 5.37 * (1 + self.composition_data['acentric_factor'][component]) 
                                                    * (1 - (self.composition_data['critical_temperature'][component]/self.t))) / 
                                    (self.p / self.composition_data['critical_pressure'][component]))
            
        return k_initial_vapour
    

    # Расчет начальных констант равновесия для жидкой фазы
    def calc_k_initial_for_liquid_wilson(self):
        k_initial_liquid = {}
        for component in list(self.composition.keys()):
            k_initial_liquid[component] = math.exp(5.37 * (1 + self.composition_data['acentric_factor'][component]) * (1 - (self.composition_data['critical_temperature'][component]/self.t))) / (self.p / self.composition_data['critical_pressure'][component])
            
        return k_initial_liquid
    

    # Расчет мольных долей в газовой фазе
    def calc_Yi_v(self, zi: dict):
        Yi_v = {}
        for component in list(self.k_values_vapour.keys()):
            Yi_v[component] = zi[component] * self.k_values_vapour[component]  
        return Yi_v


    # Расчет мольных долей в жидкой фазе
    def calc_Xi_l(self, zi: dict):
        Xi_l = {}
        for component in list(self.k_values_liquid.keys()):
            Xi_l[component] = zi[component] / self.k_values_liquid[component]    
        
        return Xi_l


    # Расчет суммы мольных долей в газовой фазе
    def calc_S_v(self, Yi_v:dict):
        return sum(list(Yi_v.values()))
    

    # Расчет суммы мольных долей в жидкой фазе
    def calc_S_l(self, Xi_l:dict):
        return sum(list(Xi_l.values()))
    

    # Нормируем мольные доли газовой фазы
    def normalize_mole_fractions_vapour(self, Yi_v:dict, S_v: float):
        normalized_mole_fractions_vapour = {}
        for component in list(Yi_v.keys()):
            normalized_mole_fractions_vapour[component] = Yi_v[component] / S_v 
        return normalized_mole_fractions_vapour


    # Нормируем мольные доли для жидкой фазы
    def normalize_mole_fractions_liquid(self, Xi_l:dict, S_l:float):
        normalized_mole_fractions_liquid = {}
        for component in list(Xi_l.keys()):
            normalized_mole_fractions_liquid[component] = Xi_l[component] / S_l 
        return normalized_mole_fractions_liquid


    # Решаем УРС для газовой фазы
    def calc_eos_for_vapour(self, y_i_v):
        eos_for_vapour = self.eos(zi=  y_i_v, components_properties= self.composition_data, p = self.p, t = self.t)
        eos_for_vapour.calc_eos()
        return eos_for_vapour


    # Решаем УРС для жидкой фазы
    def calc_eos_for_liquid(self, x_i_l):
        eos_for_liquid = self.eos(zi=x_i_l, components_properties=self.composition_data, p = self.p, t = self.t)
        eos_for_liquid.calc_eos()
        return eos_for_liquid
    

    # Рассчитываем Ri для газовой фазы
    def calc_ri_vapour(self, eos_vapour):
        ri_vapour = {}
        for component in eos_vapour.zi.keys():
            #self.initial_eos.
            ri = ((math.e ** self.initial_eos.fugacities[component]) /
                   (((math.e ** eos_vapour.fugacities[component])) * self.S_v))
            ri_vapour[component] = ri
        return ri_vapour


    # Рассчитываем Ri для жидкой фазы
    def calc_ri_liquid(self, eos_liquid):
        ri_liquid = {}
        for component in eos_liquid.zi.keys():
            ri = (((math.e ** eos_liquid.fugacities[component]))/
                  (math.e ** self.initial_eos.fugacities[component]) * self.S_l)
            ri_liquid[component] = ri 
        return ri_liquid


    # Обновление констант равновесия
    ## Для газовой фазы
    def update_k_values_vapour(self):
        new_k_i_vapour = {}
        for component in self.ri_v.keys():
            new_k_i_vapour[component] = self.k_values_vapour[component] * self.ri_v[component]
        

        return new_k_i_vapour


    ## Для жидкой фазы
    def update_k_values_liquid(self):
        new_k_i_liquid = {}
        for component in self.ri_l.keys():
            new_k_i_liquid[component] = self.k_values_liquid[component] * self.ri_l[component]
        

        return new_k_i_liquid
    

    ### Новый метод анализа стабильности 
    def check_convergence(self, e = TOL_TWO_PHASE_STABILITY_CONVERGENCE):
    

        ri_v_to_sum = []
        ri_l_to_sum = []

        for ri_v in list(self.ri_v.values()):
            ri_v_to_sum.append((ri_v-1) ** 2)

        for ri_l in list(self.ri_l.values()):
            ri_l_to_sum.append((ri_l-1) ** 2)

        sum_ri_v = sum(ri_v_to_sum)
        sum_ri_l = sum(ri_l_to_sum)

        

        if (sum_ri_v < e) or (sum_ri_l < e):
            self.convergence = True
            return True
        
        else:
            self.convergence = False
            return False
        

    def check_trivial_solution(self):
        self.trivial_solution_vapour = False
        self.trivial_solution_liquid = False

        ki_v_to_sum = []
        for ki_v in list(self.k_values_vapour.values()):
            ki_v_to_sum.append(math.pow((math.log(ki_v)),2))
        
        ki_l_to_sum = []
        for ki_l in list(self.k_values_liquid.values()):
            ki_l_to_sum.append(math.pow((math.log(ki_l)),2))

        if sum(ki_v_to_sum) < TOL_TWO_PHASE_STABILITY_CONVERGENCE_TRIVIAL_SOLUTION:
            self.trivial_solution_vapour = True



        elif sum(ki_l_to_sum) < TOL_TWO_PHASE_STABILITY_CONVERGENCE_TRIVIAL_SOLUTION:
            self.trivial_solution_liquid = True

        if self.trivial_solution_liquid and self.trivial_solution_vapour:
            self.convergence_trivial_solution = True
        else:
            self.convergence_trivial_solution = False

        

    def stability_loop(self):
        iter = 0
        self.check_convergence()
        self.check_trivial_solution()
        while (self.convergence == False) and (self.convergence_trivial_solution == False):

            self.k_values_vapour = self.update_k_values_vapour()
            self.k_values_liquid = self.update_k_values_liquid()
    
            self.Yi_v = self.calc_Yi_v(self.composition)
            self.Xi_l = self.calc_Xi_l(self.composition)

            self.S_v = self.calc_S_v(Yi_v=self.Yi_v)
            self.S_l = self.calc_S_l (Xi_l= self.Xi_l)

            self.yi_v = self.normalize_mole_fractions_vapour(self.Yi_v, self.S_v)
            self.xi_l = self.normalize_mole_fractions_liquid(self.Xi_l, self.S_l)

            self.vapour_eos = self.calc_eos_for_vapour(self.yi_v)
            self.liquid_eos = self.calc_eos_for_vapour(self.xi_l)

            self.ri_v = self.calc_ri_vapour(self.vapour_eos)
            self.ri_l = self.calc_ri_liquid(self.liquid_eos)

            iter += 1
            self.check_convergence()
            self.check_trivial_solution()



            if iter > 100000:
                break
            #raise StopIteration('PhaseStabilityIterationBreak')


    def interpetate_stability_analysis(self):

        if (((self.trivial_solution_vapour) and (self.trivial_solution_liquid)) or 
            ((self.S_v <= 1) and (self.trivial_solution_liquid)) or 
            ((self.trivial_solution_vapour) and (self.S_l <= 1)) or 
            ((self.S_v <= 1) and (self.S_l<= 1))):

            # logger.log.info('===============')
            # logger.log.info('Результат интерпритации анализа стабильности:')
            # logger.log.info(f'S_v: {self.S_v}, S_l: {self.S_l}')
            # logger.log.info('Система стабильна')
            self.stable = True
            # logger.log.info('===============')


        elif (((self.S_v > 1) and self.trivial_solution_liquid) or 
              ((self.trivial_solution_vapour) and (self.S_l> 1)) or 
                ((self.S_v > 1) and (self.S_l > 1)) or 
                ((self.S_v> 1) and (self.S_l <= 1)) or 
                ((self.S_v <= 1) and (self.S_l > 1))):
            
            # logger.log.info('===============')
            # logger.log.info('Результат интерпритации анализа стабильности:')
            # logger.log.info(f'S_v: {self.S_v}, S_l: {self.S_l}')
            # logger.log.info('Система не стабильна')
            self.stable = False
            # logger.log.info('===============')




    def calculate_phase_stability(self):
        self.initial_eos = self.calc_initial_eos()

        self.k_values_vapour = self.calc_k_initial_for_vapour_wilson()
        self.k_values_liquid = self.calc_k_initial_for_liquid_wilson()

        self.Yi_v = self.calc_Yi_v(zi = self.composition)
        self.Xi_l = self.calc_Xi_l(zi = self.composition)

        self.S_v = self.calc_S_v(Yi_v= self.Yi_v)
        self.S_l = self.calc_S_l(Xi_l= self.Xi_l)

        self.yi_v =self.normalize_mole_fractions_vapour(Yi_v=self.Yi_v, S_v= self.S_v)
        self.xi_l =self.normalize_mole_fractions_liquid(Xi_l=self.Xi_l, S_l= self.S_l)

        self.vapour_eos = self.calc_eos_for_vapour(y_i_v= self.yi_v)
        self.eos_root_chooser = EOSRootChooser(self.vapour_eos)
        self.eos_root_chooser.define_root_for_phase('vapour')
        
        self.liquid_eos = self.calc_eos_for_liquid(x_i_l= self.xi_l)
        self.eos_root_chooser = EOSRootChooser(self.liquid_eos)
        self.eos_root_chooser.define_root_for_phase('liquid')

        self.ri_v = self.calc_ri_vapour(self.vapour_eos)
        self.ri_l = self.calc_ri_liquid(self.liquid_eos)
        
        
        self.stability_loop()
        self.interpetate_stability_analysis()


        return None
    

if __name__ == '__main__':

    from calculations.Composition.Composition import Composition
    comp = Composition({'C1': 0.6, 'C6': 0.4, },
                       c6_plus_bips_correlation= None,
                       c6_plus_correlations = {'critical_temperature': 'kesler_lee',
                                                        'critical_pressure' : 'rizari_daubert',
                                                        'acentric_factor': 'Edmister',
                                                        'critical_volume': 'hall_yarborough',
                                                        'k_watson': 'k_watson',
                                                        'shift_parameter': 'jhaveri_youngren'})
    
    phs = TwoPhaseStabilityTest(comp, 7, 70, 'SRKEOS')
    phs.calculate_phase_stability()
    #phs.stability_loop()
    print(phs.convergence_trivial_solution)
    print(phs.S_v)
    print(phs.S_l)
    
    #phs.interpetate_stability_analysis()

    print(phs.k_values_vapour)
    print(phs.k_values_liquid)
    print(phs.xi_l)
    print(phs.yi_v)
    print(phs.stable)
    print(phs.initial_eos.fugacity_by_roots)
    print(phs.vapour_eos.fugacity_by_roots)