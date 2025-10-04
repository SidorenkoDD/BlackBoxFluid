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
        
    
