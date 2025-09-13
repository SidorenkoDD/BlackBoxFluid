from abc import ABC, abstractmethod

class PVTExperiment(ABC):
    
    @abstractmethod
    def calculate(self):
        pass


