from abc import ABC, abstractmethod
from dataclasses import dataclass

class Results(ABC):

    @abstractmethod
    def to_df(self):
        pass




@dataclass(frozen= True)
class TwoPhaseFlashResults:
    temperature : float
    pressure : float

    stable : bool
    EOS: str

    Fv : float | None
    Fl : float | None
    Ki: float | None

    liquid_composition: dict | None
    vapour_composition: dict | None
    
    liquid_z : float | None
    vapour_z : float | None

    vapour_molecular_mass: float | None
    liquid_molecular_mass: float | None

    vapour_volume : float | None
    liquid_volume : float | None

    vapour_molar_volume : float | None
    liquid_molar_volume : float | None

    vapour_density: float | None
    liquid_density: float | None

    vapour_viscosity : float | None
    liquid_viscosity : float | None



@dataclass
class SeparatorTestResults:

    first_stage_pressure : float
    first_stage_temperature : float
    first_stage_fv : float
    first_stage_fl : float
    first_stage_vapour_composition : dict
    first_stage_liquid_composition : dict
    first_stage_vapour_z : float
    first_stage_liquid_z : float
    first_stage_k_values : dict
    first_stage_vapour_mw : float
    first_stage_liquid_mw : float
    first_stage_vapour_volume : float
    first_stage_liquid_volume : float
    first_stage_vapour_density : float
    first_stage_liquid_density : float

    second_stage_pressure : float
    second_stage_temperature : float
    second_stage_fv : float
    second_stage_fl : float
    second_stage_vapour_composition : dict
    second_stage_liquid_composition : dict
    second_stage_vapour_z : float
    second_stage_liquid_z : float
    second_stage_k_values : dict
    second_stage_vapour_mw : float
    second_stage_liquid_mw : float
    second_stage_vapour_volume : float
    second_stage_liquid_volume : float
    second_stage_vapour_density : float
    second_stage_liquid_density : float

    third_stage_pressure : float
    third_stage_temperature : float
    third_stage_fv : float
    third_stage_fl : float
    third_stage_vapour_composition : dict
    third_stage_liquid_composition : dict
    third_stage_vapour_z : float
    third_stage_liquid_z : float
    third_stage_k_values : dict
    third_stage_vapour_mw : float
    third_stage_liquid_mw : float
    third_stage_vapour_volume : float
    third_stage_liquid_volume : float
    third_stage_vapour_density : float
    third_stage_liquid_density : float



@dataclass
class StandardSeparationResults:
    p_res : float
    p_sat : float
    p_stc : float

    t_res : float

    liquid_density_p_res : float
    liquid_density_p_sat : float
    liquid_density_separated : float

    bo_p_res : float
    bo_p_sat : float

    separated_gas_dens : float

    rs : float


@dataclass
class DLEResults:
    index : float
    pressure_arr : list
    temperature_arr : list

    liquid_volume_arr : list
    gas_volume_arr : list

    liquid_density_arr : list
    gas_density_arr : list

    fl_arr : list
    fv_arr : list

    liquid_z : list
    gas_z : list

    liquid_compositions : list
    gas_compositions : list

    liquid_viscosity : list
    gas_viscosity : list

    bo : list
    rs : list


@dataclass
class CCEResults:
    pressure : list
    temperature : float
    liquid_volume : list
    liquid_density : list
    # v_div_vres : list
    # v_div_vsat : list

