from Utils.Constants import CONSTANT_R
from EOS.BrusilovskiyEOSV2 import BrusilovskiyEOS
from Utils.Viscosity import ViscosityFactory


class FluidPropertiesCalculator:
    def __init__(self, composition: dict, composition_properties: dict, eos_object: BrusilovskiyEOS, p: float, T: float,
                 viscosity_method: str = 'LBC'):
        self._composition = composition
        self._composition_properties = composition_properties
        self._eos = eos_object
        self._p = p
        self._T = T
        self._viscosity_method = viscosity_method

    @property
    def molar_mass(self):
        M = 0.0

        for component in self._composition:
            M += self._composition[component] * self._composition_properties['molar_mass'][component]

        return M

    @property
    def molar_volume(self):
        return CONSTANT_R * self._T * self._eos.z / self._p - self._eos.shift_parametr

    @property
    def molar_density(self):
        return 1 / self.molar_volume

    @property
    def density(self):
        return self.molar_density * self.molar_mass

    @property
    def z_shift(self):
        return self._eos.z - self._p * self._eos.shift_parametr / (self._T * CONSTANT_R)

    @property
    def viscosity(self):
        visc = ViscosityFactory().create_viscosity_object(self._viscosity_method)
        return visc(mole_fractions=self._composition, composition_data=self._composition_properties,
                   phase_density=self.density, mw=self.molar_mass, temperature=self._T,
                    alpha0=0.12538570165634155,
                    alpha1=0.02722247689962387,
                    alpha2=0.004341159015893936,
                    alpha3=-0.004339530132710934,
                    alpha4=0.0007456476450897753,
                    ).calculate()

        # return visc(mole_fractions=self._composition, composition_data=self._composition_properties,
        #             phase_density=self.density, mw=self.molar_mass, temperature=self._T,
        #             alpha0=0.1314433068037033,
        #             alpha1=0.015912599861621857,
        #             alpha2=0.05853300169110298,
        #             alpha3=-0.04075799882411957,
        #             alpha4=0.009332399815320969,
        #             ).calculate()
        # return visc(mole_fractions=self._composition, composition_data=self._composition_properties,
        #             phase_density=self.density, mw=self.molar_mass, temperature=self._T).calculate()
