import numpy as np
from calculations.EOS.BaseEOS import EOS
from calculations.Composition.Composition import Composition
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation
from calculations.PhaseDiagram.DewPressure import DewPressureCalculation



class PhaseEnvelope:


    def __init__(self, zi:Composition, p_max, t_max, t_min = 0, t_step=10):
        self.zi = zi
        self.p_max = p_max
        self.t_max = t_max
        self.t_min = t_min
        self.t_step = t_step
        self.temp_range = np.arange(self.t_min + 273.14, self.t_max +273.14, self.t_step)
        self.results = {}


    def _calc_phase_envelope(self, eos:EOS):


        for temp in self.temp_range:
            cur_saturation_pressure_obj = SaturationPressureCalculation(self.zi, p_max= self.p_max, temp=temp)
            cur_dew_pressure_obj = DewPressureCalculation(self.zi, self.p_max, temp)

            pb = cur_saturation_pressure_obj.sp_convergence_loop(eos)
            pd = cur_dew_pressure_obj.dp_convergence_loop(eos)

            self.results[temp] = [pb, pd]

        print(self.results)
        
