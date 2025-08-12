from abc import ABC, abstractmethod
from dataclasses import dataclass

class Results(ABC):

    @abstractmethod
    def to_df(self):
        pass



# class FlashResults(ABC, Results):
#     def __init__(self):
#         super().__init__()

#     def get_results(self):
#         return super().get_results()
    


@dataclass(frozen= True)
class TwoPhaseFlashResults:
    temperature : float
    pressure : float
    
    stable : bool
    
    Fv : float | None
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

    


# class OnePhaseFlashResults(FlashResults):

#     def __init__(self, flash_obj):
#         self.flash_obj = flash_obj

#     def get_results(self):
#         return super().get_results()
    


# class TwoPhaseFlashResults(FlashResults):

#     def __init__(self, flash_obj):
#         self.flash_obj = flash_obj

#     def get_results(self):
#         return super().get_results()
