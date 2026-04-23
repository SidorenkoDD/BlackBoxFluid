import math
from ..Composition.CompositionV2 import Composition
from .BaseEOS import EOS
from ..Utils.Constants import CONSTANT_R
from ..Utils.Cardano import cubic_roots_cardano


class BrusilovskiyEOS(EOS):
    def __init__(self, composition: Composition, p: float, t: float):
        super().__init__(composition, p, t)

        # self._composition = composition

        self.shift_parametr = None
        self.choosen_fugacities = None
        self.choosen_eos_root = None
        self.normalized_gibbs_energy = None
        self.fugacity_by_roots = None
        self.fugacity_coef_by_roots = None
        self.real_roots_eos = None

        self._zi = composition.composition
        self._components_properties = composition.composition_data
        self._p = p
        self._t = t

        self._A_mixture = None
        self._B_mixture = None
        self._C_mixture = None
        self._D_mixture = None

        self._cache_A = {}
        self._cache_B = {}
        self._cache_C = {}
        self._cache_D = {}

        self._cache_Aij = {}
        self._cache_dz_dxk = {}
        self._cache_dAm_dxk = {}
        self._cache_dz_dp = None

    #                          |||  РАСЧЕТ КОЭФФИЦИЕНТОВ УРС  |||
    #                          VVV                            VVV
    # =====================================================================================
    # region

    def _calc_A_of_component(self, component: str):
        A = self._cache_A.get(component)
        if A is not None:
            return A

        a = self._components_properties['a'][component]
        A = a * self._p / math.pow((CONSTANT_R * self._t), 2)

        self._cache_A[component] = A
        return A

    def _calc_B_of_component(self, component: str):
        B = self._cache_B.get(component)
        if B is not None:
            return B

        b = self._components_properties['b'][component]
        B = b * self._p / (CONSTANT_R * self._t)

        self._cache_B[component] = B
        return B

    def _calc_C_of_component(self, component: str):
        C = self._cache_C.get(component)
        if C is not None:
            return C

        c = self._components_properties['c'][component]
        C = c * self._p / (CONSTANT_R * self._t)

        self._cache_C[component] = C
        return C

    def _calc_D_of_component(self, component: str):
        D = self._cache_D.get(component)
        if D is not None:
            return D

        d = self._components_properties['d'][component]
        D = d * self._p / (CONSTANT_R * self._t)

        self._cache_D[component] = D
        return D

    def _calc_Aij(self, component_i: str, component_j: str):
        _cached_Aij = self._cache_Aij.get(component_i, {}).get(component_j, None)
        if _cached_Aij is not None:
            return _cached_Aij

        A1 = self._calc_A_of_component(component_i)
        A2 = self._calc_A_of_component(component_j)
        bip = self._components_properties['bip'][component_i][component_j]
        A_ij = math.sqrt(A1 * A2) * (1 - bip)

        self._cache_Aij.setdefault(component_i, {}).setdefault(component_j, A_ij)
        self._cache_Aij.setdefault(component_j, {}).setdefault(component_i, A_ij)
        return A_ij

    def _calc_A_mixture(self):
        if self._A_mixture is not None:
            return self._A_mixture

        first_set_of_comps = list(self._zi.keys())
        second_set_of_comps = list(self._zi.keys())

        A_m = 0.0

        for comp1 in first_set_of_comps:
            for comp2 in second_set_of_comps:
                z1 = self._zi[comp1]
                z2 = self._zi[comp2]
                A_ij = self._calc_Aij(comp1, comp2)
                A_m += z1 * z2 * A_ij

        self._A_mixture = A_m

        return self._A_mixture

    def _calc_B_mixture(self):
        if self._B_mixture is not None:
            return self._B_mixture

        B_m = 0.0

        for comp in list(self._zi.keys()):
            z = self._zi[comp]
            B = self._calc_B_of_component(comp)
            B_m += z * B

        self._B_mixture = B_m
        return self._B_mixture

    def _calc_C_mixture(self):
        if self._C_mixture is not None:
            return self._C_mixture

        C_m = 0.0

        for comp in list(self._zi.keys()):
            z = self._zi[comp]
            C = self._calc_C_of_component(comp)
            C_m += z * C

        self._C_mixture = C_m
        return self._C_mixture

    def _calc_D_mixture(self):
        if self._D_mixture is not None:
            return self._D_mixture

        D_m = 0.0

        for comp in list(self._zi.keys()):
            z = self._zi[comp]
            D = self._calc_D_of_component(comp)
            D_m += z * D

        self._D_mixture = D_m
        return self._D_mixture

    def _calc_roots_eos(self):
        A_m = self._calc_A_mixture()
        B_m = self._calc_B_mixture()
        C_m = self._calc_C_mixture()
        D_m = self._calc_D_mixture()

        E_0 = C_m + D_m - B_m - 1
        E_1 = A_m - B_m * C_m + C_m * D_m - B_m * D_m - D_m - C_m
        E_2 = -(B_m * C_m * D_m + C_m * D_m + A_m * B_m)

        real_roots_eos = cubic_roots_cardano(1.0, E_0, E_1, E_2, only_real_roots=True)

        return real_roots_eos

    # endregion
    # =====================================================================================

    #                          |||  РАСЧЕТ ЛЕТУЧЕСТИ И ЭНЕРГИИ ГИББСА  |||
    #                          VVV                                     VVV
    # =====================================================================================
    # region

    def _calc_fugacity_logarithm_for_component_BRS(self, component, root):
        """
        Возвращает натуральный логарифм летучести компонента для данного к-та сверхсжимаемости z.
        """

        xi = self._zi[component]
        p = self._p
        z = root

        B_m = self._B_mixture

        if z <= B_m:
            return 0.0, 0.0

        ln_phi_i = self._calc_fugacity_coef_logarithm_for_component_BRS(component, root)

        lnfi = ln_phi_i + math.log(xi * p)

        return lnfi, ln_phi_i

    def _calc_fugacity_coef_logarithm_for_component_BRS(self, component, root):
        """
        Возвращает натуральный логарифм коэффициента летучести компонента для данного к-та сверхсжимаемости z.
        """

        z = root

        A_m = self._A_mixture
        B_m = self._B_mixture
        B_i = self._cache_B.get(component)
        C_m = self._C_mixture
        C_i = self._cache_C.get(component)
        D_m = self._D_mixture
        D_i = self._cache_D.get(component)

        sum_xi_Aij = 0.5 * self._calc_dA_mixture_dxk(component)

        part1 = -math.log(z - B_m)
        part2 = - A_m / (C_m - D_m) * ((2 * sum_xi_Aij) / A_m - (C_i - D_i) / (C_m - D_m)) * math.log(
            (z + C_m) / (z + D_m))
        part3 = B_i / (z - B_m)
        part4 = - A_m / (C_m - D_m) * (C_i / (z + C_m) - D_i / (z + D_m))

        ln_phi_i = part1 + part2 + part3 + part4

        return ln_phi_i

    def _calc_fugacity_by_roots(self):
        fugacity_by_roots = {}
        fugacity_coef_by_roots = {}

        for root in self.real_roots_eos:

            fugacity_by_components = {}
            fugacity_coef_by_components = {}

            for component in self._zi.keys():

                ln_fi, ln_phi_i = self._calc_fugacity_logarithm_for_component_BRS(component, root)
                fugacity_by_components[component] = ln_fi
                fugacity_coef_by_components[component] = ln_phi_i

            fugacity_by_roots[root] = fugacity_by_components
            fugacity_coef_by_roots[root] = fugacity_coef_by_components

        return fugacity_by_roots, fugacity_coef_by_roots

    def _calc_normalized_gibbs_energy(self) -> dict:
        """
        Метод возвращает словарь {корень УРС: значение приведенной энергии Гиббса}
        """
        B_m = self._B_mixture
        normalized_gibbs_energy = {}
        for root in self.fugacity_by_roots:
            gibbs_energy_by_roots = []

            if root <= 0:
                normalized_gibbs_energy[root] = math.inf

            elif root <= B_m:
                normalized_gibbs_energy[root] = math.inf

            else:
                for component in self.fugacity_by_roots[root].keys():
                    gibbs_energy_by_roots.append(self.fugacity_by_roots[root][component] * self._zi[component])
                normalized_gibbs_energy[root] = sum(gibbs_energy_by_roots)

        return normalized_gibbs_energy

    def _choose_eos_root_by_gibbs_energy(self):
        """
        return: Значение корня Z, при котором энергия Гиббса минимальна
        """

        min_gibbs_energy = min(self.normalized_gibbs_energy.values())
        return [k for k, v in self.normalized_gibbs_energy.items() if v == min_gibbs_energy][0]

    # endregion
    # =====================================================================================

    #                          |||  РАСЧЕТ ПРОИЗВОДНОЙ ЛЕТУЧЕСТИ  |||
    #                          VVV                                VVV
    # =====================================================================================
    # region

    def calc_d_log_phi_i_dxk(self, component_i: str, component_k: str):

        z = self._z

        A_m = self._A_mixture
        B_i = self._cache_B.get(component_i)
        B_m = self._B_mixture
        C_i = self._cache_C.get(component_i)
        C_m = self._C_mixture
        D_i = self._cache_D.get(component_i)
        D_m = self._D_mixture

        A_ik = self._cache_Aij.get(component_i, {}).get(component_k)
        sum_xi_Aij = 0.5 * self._cache_dAm_dxk.get(component_i)

        dz_dxk = self._calc_dz_dxk(component_k)
        dAm_dxk = self._cache_dAm_dxk.get(component_k)
        dBm_dxk = self._cache_B.get(component_k)
        dCm_dxk = self._cache_C.get(component_k)
        dDm_dxk = self._cache_D.get(component_k)

        deriv_part1 = (dz_dxk - dBm_dxk) / (z - B_m)

        deriv_part21 = (dAm_dxk * (C_m - D_m) - A_m * (dCm_dxk - dDm_dxk)) / math.pow(C_m - D_m, 2)
        deriv_part22 = (2 * (A_ik * A_m - dAm_dxk * sum_xi_Aij) / math.pow(A_m, 2) +
                        ((C_i - D_i) * (dCm_dxk - dDm_dxk)) / math.pow(C_m - D_m, 2))
        deriv_part23 = ((z + D_m) / (z + C_m)) * (
                ((dz_dxk + dCm_dxk) * (z + D_m) - (dz_dxk + dDm_dxk) * (z + C_m)) / math.pow(z + D_m, 2))
        part21 = A_m / (C_m - D_m)
        part22 = (2 * sum_xi_Aij) / A_m - (C_i - D_i) / (C_m - D_m)
        part23 = math.log((z + C_m) / (z + D_m))
        deriv_part2 = deriv_part21 * part22 * part23 + part21 * deriv_part22 * part23 + part21 * part22 * deriv_part23

        deriv_part3 = (-B_i * (dz_dxk - dBm_dxk)) / math.pow(z - B_m, 2)

        part41 = part21
        part42 = C_i / (z + C_m) - D_i / (z + D_m)
        deriv_part41 = deriv_part21
        deriv_part42 = ((-C_i * (dz_dxk + dCm_dxk) / math.pow(z + C_m, 2)) -
                        (-D_i * (dz_dxk + dDm_dxk) / math.pow(z + D_m, 2)))
        deriv_part4 = deriv_part41 * part42 + deriv_part42 * part41

        result = -deriv_part1 - deriv_part2 + deriv_part3 - deriv_part4

        return result

    def calc_d_log_phi_i_dp(self, component_i: str):
        z = self._z

        A_m = self._A_mixture
        B_i = self._cache_B.get(component_i)
        B_m = self._B_mixture
        C_i = self._cache_C.get(component_i)
        C_m = self._C_mixture
        D_i = self._cache_D.get(component_i)
        D_m = self._D_mixture

        sum_xj_Aij = 0.5 * self._cache_dAm_dxk.get(component_i)

        dBm_dp = self._B_mixture / self._p
        dCm_dp = self._C_mixture / self._p
        dCi_dp = C_i / self._p
        dDm_dp = self._D_mixture / self._p
        dDi_dp = D_i / self._p

        dz_dp = self._calc_dz_dp()

        part1 = (1 / (z - B_m)) * ((dz_dp - dBm_dp) * (1 + B_i / (z - B_m)) - dBm_dp)

        part21 = (2 * sum_xj_Aij / A_m - (C_i - D_i) / (C_m - D_m)) * ((dz_dp + dCm_dp) / (z + C_m) - (dz_dp + dDm_dp) / (z + D_m))
        part22 = 1 / math.pow(z + C_m, 2) * (dCi_dp * (z + C_m) - C_i * (dz_dp + dCm_dp))
        part23 = 1 / math.pow(z + D_m, 2) * (dDi_dp * (z + D_m) - D_i * (dz_dp + dDm_dp))

        part2 = A_m / (C_m - D_m) * (part21 + part22 - part23)

        result = - part1 - part2

        return result

    def _calc_dfi_dxk(self, component_i: str, component_k: str):
        p = self._p
        xi = self._zi[component_i]
        log_phi_i = self.fugacity_coef_by_roots[self._z][component_i]
        d_log_phi_i_dxk = self.calc_d_log_phi_i_dxk(component_i, component_k)

        phi_i = math.exp(log_phi_i)

        return p * phi_i * (component_i == component_k) + p * xi * phi_i * d_log_phi_i_dxk

    def _calc_dA_mixture_dxk(self, component_k: str):
        dAm_dxk = self._cache_dAm_dxk.get(component_k, None)
        if dAm_dxk is not None:
            return dAm_dxk

        result = 0.0
        for component_j in list(self._zi.keys()):
            z_j = self._zi[component_j]
            A_kj = self._cache_Aij[component_k][component_j]
            result += z_j * A_kj

        result *= 2
        self._cache_dAm_dxk[component_k] = result
        return result

    def _calc_dE0_dxk(self, component_k: str):
        dBm_dxk = self._cache_B.get(component_k)
        dCm_dxk = self._cache_C.get(component_k)
        dDm_dxk = self._cache_D.get(component_k)

        return dCm_dxk + dDm_dxk - dBm_dxk

    def _calc_dE1_dxk(self, component_k: str):
        dAm_dxk = self._cache_dAm_dxk.get(component_k)
        dBm_dxk = self._cache_B.get(component_k)
        dCm_dxk = self._cache_C.get(component_k)
        dDm_dxk = self._cache_D.get(component_k)

        B_m = self._B_mixture
        C_m = self._C_mixture
        D_m = self._D_mixture

        return (dAm_dxk - dDm_dxk - dCm_dxk - C_m * dBm_dxk - B_m * dCm_dxk + C_m * dDm_dxk + D_m * dCm_dxk -
                B_m * dDm_dxk - D_m * dBm_dxk)

    def _calc_dE2_dxk(self, component_k: str):
        dAm_dxk = self._cache_dAm_dxk.get(component_k)
        dBm_dxk = self._cache_B.get(component_k)
        dCm_dxk = self._cache_C.get(component_k)
        dDm_dxk = self._cache_D.get(component_k)

        A_m = self._A_mixture
        B_m = self._B_mixture
        C_m = self._C_mixture
        D_m = self._D_mixture

        return - (dBm_dxk * C_m * D_m + dCm_dxk * B_m * D_m + dDm_dxk * C_m * B_m + dCm_dxk * D_m + C_m * dDm_dxk +
                  dAm_dxk * B_m + A_m * dBm_dxk)

    def _calc_dz_dxk(self, component_k: str):
        dz_dxk = self._cache_dz_dxk.get(component_k, None)
        if dz_dxk is not None:
            return dz_dxk

        z = self._z

        A_m = self._A_mixture
        B_m = self._B_mixture
        C_m = self._C_mixture
        D_m = self._D_mixture

        E_0 = C_m + D_m - B_m - 1
        E_1 = A_m - B_m * C_m + C_m * D_m - B_m * D_m - D_m - C_m

        numerator = self._calc_dE0_dxk(component_k) * math.pow(z, 2) + self._calc_dE1_dxk(
            component_k) * z + self._calc_dE2_dxk(component_k)
        denominator = 3 * math.pow(z, 2) + 2 * E_0 * z + E_1

        dz_dxk = -(numerator / denominator)
        self._cache_dz_dxk[component_k] = dz_dxk
        return dz_dxk

    def _calc_dz_dp(self):
        if self._cache_dz_dp is not None:
            return self._cache_dz_dp

        z = self._z

        A_m = self._A_mixture
        B_m = self._B_mixture
        C_m = self._C_mixture
        D_m = self._D_mixture

        E_0 = C_m + D_m - B_m - 1
        E_1 = A_m - B_m * C_m + C_m * D_m - B_m * D_m - D_m - C_m

        E_00 = C_m + D_m - B_m
        E_11 = A_m - 2 * B_m * C_m + 2 * C_m * D_m - 2 * B_m * D_m - D_m - C_m
        E_22 = -(3 * B_m * C_m * D_m + 2 * C_m * D_m + 2 * A_m * B_m)

        numerator = E_00 * math.pow(z, 2) + E_11 * z + E_22
        numerator /= self._p
        denominator = 3 * math.pow(z, 2) + 2 * E_0 * z + E_1

        self._cache_dz_dp = -(numerator / denominator)
        return self._cache_dz_dp


    # endregion
    # =====================================================================================

    def calc_eos(self):
        """
        Метод рассчитывает коэффициенты уравнения состояния, используя заданные состав и свойства компонент, рассчитывает
        Z-фактор, определяет летучести. Возвращает найденное значение Z-фактора, а также значения летучести для
        каждого компонента в виде словаря (dict).
        """
        self.clear_cache()

        self.real_roots_eos = self._calc_roots_eos()

        self.fugacity_by_roots, self.fugacity_coef_by_roots = self._calc_fugacity_by_roots()
        self.normalized_gibbs_energy = self._calc_normalized_gibbs_energy()
        self.choosen_eos_root = self._choose_eos_root_by_gibbs_energy()
        self.choosen_fugacities = self.fugacity_by_roots[self.choosen_eos_root]
        self.shift_parametr = self._calc_shift_parametr()

        self._z = self.choosen_eos_root
        self._fugacities = self.choosen_fugacities

        return self.choosen_eos_root, self.choosen_fugacities

    def clear_cache(self):
        self._A_mixture = None
        self._B_mixture = None
        self._C_mixture = None
        self._D_mixture = None

        self._cache_A = {}
        self._cache_B = {}
        self._cache_C = {}
        self._cache_D = {}

        self._cache_Aij = {}
        self._cache_dz_dxk = {}
        self._cache_dAm_dxk = {}

    # Для совместимости
    def _calc_shift_parametr(self) -> float:
        '''Calculation of shift parameter  for EOS

        Returns
        ------
            shift parameter
        '''
        c_to_sum = []
        for component in self._zi.keys():
            zi = self._zi[component]
            bi = self._components_properties['b'][component]
            shift = self._components_properties['shift_parameter'][component]
            c_to_sum.append(zi * bi * shift)

        return sum(c_to_sum)

    @property
    def z(self):
        """
        Возвращает значение рассчитанного коэффициента сверхсжимаемости
        """
        return self._z

    @property
    def fugacities(self):
        return self._fugacities


if __name__ == '__main__':
    pass
