from pathlib import Path
import sys

from calculations.Composition.Composition import Composition
from calculations.VLE.flash import FlashFactory
from calculations.Utils.Conditions import Conditions
from calculations.PhaseDiagram.PhaseDiagram_v4 import PhaseDiagram, SaturationPressure
from calculations.Experiments.ExperimentsFacade import ExperimentsFacade
from calculations.PhaseDiagram.SaturationPressure import SaturationPressureCalculation
from calculations.PhaseDiagram.PhaseEnvelope import PhaseEnvelope


root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))



class CompositionalModel:
    def __init__(self,zi: Composition,
                 eos: str = 'PREOS',
                 viscosity_method = 'LBC'):
        self._composition = zi
        self._eos = eos
        self._viscosity_method = viscosity_method
        self._flash_results = {}
        self.experiments = ExperimentsFacade(self._composition, self._eos)
        self.PHASE_ENVELOPE = PhaseEnvelope(self._composition, 50, 250)
        from calculations.Utils.Export import E300
        self.EXPORT = E300(self)


    def flash(self, conditions, flash_type = 'TwoPhaseFlash'):
        self._flash_object = FlashFactory(self._composition, self._eos, viscosity_method= self._viscosity_method)
        flash_calculator = self._flash_object.create_flash(flash_type=flash_type)
        result = flash_calculator.calculate(conditions=conditions)

        self._flash_results[str(flash_type) + '_' + str(conditions.p)+'_' + str(conditions.t - 273.14)] = result 
    
    
    def plot_phase_diagram(self, p_max = 40, t_min = 0, t_max = 200, t_step = 10):
        self._phase_diagram_obj = PhaseDiagram(self._composition, p_max= p_max, t_min= t_min, t_max= t_max, t_step= t_step)
        self._phase_diagram_obj.calc_phase_diagram(eos = self._eos)
        self._phase_diagram_obj.plot_phase_diagram()


    def saturation_pressure(self,t, p_max= 40):
        self._sat_pres_obj = SaturationPressureCalculation(self._composition, p_max, t)
        self._sat_pres_obj.sp_convergence_loop(eos = self._eos)
        print('SATURATION PRESSURE CALCULATION')
        print('=====')
        print(f'CALCULATED SATURATION PRESSURE: {self._sat_pres_obj.p_b * 10} bar')
        print(f'TEMPERATURE: {t} C')


    @property
    def show_flashes(self):
        return self._flash_results


if __name__ == '__main__':


    diii_zi_norm = {'CO2': 0.00215083887911224,
                    'C1': 0.282009963534675,
                    'C2': 0.149068137018216,
                    'C3': 0.115134903302074,
                    'iC4': 0.0142855717984413,
                    'nC4': 0.0372145171943236,
                    'iC5': 0.0117745929987574,
                    'nC5': 0.0113044093184266,
                    'C6': 0.0190074143626122,
                    'C7': 0.0308220212682833,
                    'C8': 0.0415061899850774,
                    'C9': 0.0340032604384294,
                    'C10': 0.030872041037113,
                    'C11': 0.0252598520737042,
                    'C12': 0.021408351340502,
                    'C13': 0.0206180432863297,
                    'C14': 0.0181270714401026,
                    'C15': 0.0133852207298811,
                    'C16': 0.0113444244179341,
                    'C17': 0.00953371880408519,
                    'C18': 0.00949370251198387,
                    'C19': 0.00999389781509374,
                    'C20': 0.00667260221888989,
                    'C21': 0.0062324307576351,
                    'C22': 0.00585228254193848,
                    'C23': 0.00495193117522979,
                    'C24': 0.00469183034509487,
                    'C25': 0.00408159172944863,
                    'C26': 0.0036114083472663,
                    'C27': 0.00342133483571489,
                    'C28': 0.00300117062606541,
                    'C29': 0.00278108459728957,
                    'C30': 0.00240093638159295,
                    'C31': 0.00234091298696055,
                    'C32': 0.00212082725633315,
                    'C33': 0.00195076084731283,
                    'C34': 0.00180070243526894,
                    'C35': 0.00170066349390634,
                    'C36': 0.0240693858688939}
    
    comp = Composition(diii_zi_norm)

        # Изменение свойств компонент
    comp.edit_component_properties('CO2', {'critical_pressure': 7.3764,
                                                    'critical_temperature': 306.19,
                                                    })

    comp.edit_component_properties('C1', {'critical_pressure': 4.600154768,
                                                    'critical_temperature': 190.5900061,
                                                    'acentric_factor':0.008})

    comp.edit_component_properties('C2', {'critical_pressure': 4.883865077,
                                                    'critical_temperature': 305.3899939,
                                                    'acentric_factor':0.097999997})

    comp.edit_component_properties('C3', {'critical_pressure': 4.245518041,
                                                    'critical_temperature': 369.7899878,
                                                    'acentric_factor':0.151999995})

    comp.edit_component_properties('iC4', {'critical_pressure': 3.64770116,
                                                    'critical_temperature': 408.089,
                                                    'acentric_factor':0.175999999})

    comp.edit_component_properties('nC4', {'critical_pressure': 3.799687887,
                                                    'critical_temperature': 425.1900122,
                                                    'acentric_factor':0.193000004})

    comp.edit_component_properties('iC5', {'critical_pressure': 3.384255155,
                                                    'critical_temperature': 460.3899939,
                                                    'acentric_factor':0.226999998})

    comp.edit_component_properties('nC5', {'critical_pressure': 3.374122036,
                                                    'critical_temperature': 469.5899451,
                                                    'acentric_factor':0.250999987})

    comp.edit_component_properties('C6', {'critical_pressure': 2.968822229,
                                                    'critical_temperature': 507.3899939,
                                                    'acentric_factor':0.296000004})

    comp.edit_component_properties('C7', {'critical_pressure': 2.9451884,
                                                    'critical_temperature': 536.4781592,
                                                    'acentric_factor':0.337441325})

    comp.edit_component_properties('C8', {'critical_pressure': 2.741522808,
                                                    'critical_temperature': 558.0327856,
                                                    'acentric_factor':0.374272853
    })

    comp.edit_component_properties('C9', {'critical_pressure': 2.506488844
    ,
                                                    'critical_temperature': 582.0675757
    ,
                                                    'acentric_factor':0.420477808
    })

    comp.edit_component_properties('C10', {'critical_pressure': 2.329497094
    ,
                                                    'critical_temperature': 602.5048926
    ,
                                                    'acentric_factor':0.462806612
    })

    comp.edit_component_properties('C11', {'critical_pressure': 2.177428424
    ,
                                                    'critical_temperature': 621.215769
    ,
                                                    'acentric_factor':0.504519641
    })

    comp.edit_component_properties('C12', {'critical_pressure': 2.057186543
    ,
                                                    'critical_temperature': 640.9806616
    ,
                                                    'acentric_factor':0.548880339
    })

    comp.edit_component_properties('C13', {'critical_pressure': 1.960886164
    ,
                                                    'critical_temperature': 659.8851416
    ,
                                                    'acentric_factor':0.583677530288696
    })

    comp.edit_component_properties('C14', {'critical_pressure': 1.870848251
    ,
                                                    'critical_temperature': 678.9091284
    ,
                                                    'acentric_factor':0.626245558261871
    })

    comp.edit_component_properties('C15', {'critical_pressure': 1.785777366
    ,
                                                    'critical_temperature': 697.9627783
    ,
                                                    'acentric_factor':0.67011171579361
    })

    comp.edit_component_properties('C16', {'critical_pressure': 1.716160106
    ,
                                                    'critical_temperature': 716.3793433
    ,
                                                    'acentric_factor':0.712403476238251
    })

    comp.edit_component_properties('C17', {'critical_pressure': 1.6502672
    ,
                                                    'critical_temperature': 732.3194067
    ,
                                                    'acentric_factor':0.75047355890274
    })

    comp.edit_component_properties('C18', {'critical_pressure': 1.603241119
    ,
                                                    'critical_temperature': 747.2742407
    ,
                                                    'acentric_factor':0.78474098443985
    })

    comp.edit_component_properties('C19', {'critical_pressure': 1.574782599
    ,
                                                    'critical_temperature': 760.3541968
    ,
                                                    'acentric_factor':0.813140332698822
    })

    comp.edit_component_properties('C20', {'critical_pressure': 1.544921768
    ,
                                                    'critical_temperature': 772.8315527
    ,
                                                    'acentric_factor':0.840511083602905
    })

    comp.edit_component_properties('C21', {'critical_pressure': 1.508275892
    ,
                                                    'critical_temperature': 789.0159399
    ,
                                                    'acentric_factor':0.875432074069977
    })

    comp.edit_component_properties('C22', {'critical_pressure': 1.480574379
    ,
                                                    'critical_temperature': 802.944834
    ,
                                                    'acentric_factor':0.904504716396332
    })

    comp.edit_component_properties('C23', {'critical_pressure': 1.456971762
    ,
                                                    'critical_temperature': 815.6217139
    ,
                                                    'acentric_factor':0.93022620677948
    })

    comp.edit_component_properties('C24', {'critical_pressure': 1.435632534
    ,
                                                    'critical_temperature': 828.1141455
    ,
                                                    'acentric_factor':0.954706072807312
    })

    comp.edit_component_properties('C25', {'critical_pressure': 1.414600496
    ,
                                                    'critical_temperature': 841.3556616
    ,
                                                    'acentric_factor':0.979655742645264
    })

    comp.edit_component_properties('C26', {'critical_pressure': 1.395581669
    ,
                                                    'critical_temperature': 854.4172461
    ,
                                                    'acentric_factor':1.00312113761902
    })

    comp.edit_component_properties('C27', {'critical_pressure': 1.37692318
    ,
                                                    'critical_temperature': 868.2071631
    ,
                                                    'acentric_factor':1.02658879756927
    })

    comp.edit_component_properties('C28', {'critical_pressure': 1.361332726
    ,
                                                    'critical_temperature': 880.939646
    ,
                                                    'acentric_factor':1.04691398143768
    })

    comp.edit_component_properties('C29', {'critical_pressure': 1.346311139
    ,
                                                    'critical_temperature': 893.4580786
    ,
                                                    'acentric_factor':1.06568455696106
    })

    comp.edit_component_properties('C30', {'critical_pressure': 1.332525464
    ,
                                                    'critical_temperature': 905.845896
    ,
                                                    'acentric_factor':1.08289325237274
    })

    comp.edit_component_properties('C31', {'critical_pressure': 1.320621388
    ,
                                                    'critical_temperature': 918.1856177
    ,
                                                    'acentric_factor':1.0985347032547
    })

    comp.edit_component_properties('C32', {'critical_pressure':1.30892188
    ,
                                                    'critical_temperature': 930.3385107
    ,
                                                    'acentric_factor':1.11257469654083

    })

    comp.edit_component_properties('C33', {'critical_pressure':1.298114857,
                                                    'critical_temperature': 942.3852637
    ,
                                                    'acentric_factor':1.12501060962677

    })

    comp.edit_component_properties('C34', {'critical_pressure':1.288114316,
                                                    'critical_temperature': 954.3325903
    ,
                                                    'acentric_factor':1.13583159446716
    })

    comp.edit_component_properties('C35', {'critical_pressure':1.278844403,
                                                    'critical_temperature':966.1865942
    ,
                                                    'acentric_factor':1.14502727985382
    })

    comp.edit_component_properties('C36', {'critical_pressure':1.270238925,
                                                    'critical_temperature':977.9528296
    ,
                                                    'acentric_factor':1.15258979797363
    })


    model1 = CompositionalModel(comp)

    conds2 = Conditions(14,400)

    model1.flash(conds2)
    print(model1.show_flashes)




