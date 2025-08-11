from abc import ABC, abstractmethod
from Flash import Flash


class Results(ABC):

    @abstractmethod
    def get_results(self):
        pass



class FlashResults(ABC, Results):

    def get_results(self):
        return super().get_results()
    

class OnePhaseFlashResults(FlashResults):

    def __init__(self, flash_obj):
        self.flash_obj = flash_obj

    def get_results(self):
        return super().get_results()
    


class TwoPhaseFlashResults(FlashResults):

    def __init__(self, flash_obj):
        self.flash_obj = flash_obj

    def get_results(self):
        return super().get_results()
