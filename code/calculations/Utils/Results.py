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

    vapour_density: float | None
    liquid_density: float | None


    def show_compositions(self):
        ...
        
    

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

    second_stage_pressure : float
    second_stage_temperature : float
    second_stage_fv : float
    second_stage_fl : float
    second_stage_vapour_composition : dict
    second_stage_liquid_composition : dict
    second_stage_vapour_z : float
    second_stage_liquid_z : float
    second_stage_k_values : dict

    third_stage_pressure : float
    third_stage_temperature : float
    third_stage_fv : float
    third_stage_fl : float
    third_stage_vapour_composition : dict
    third_stage_liquid_composition : dict
    third_stage_vapour_z : float
    third_stage_liquid_z : float
    third_stage_k_values : dict
