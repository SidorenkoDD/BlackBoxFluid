# flash_calculator.py
from constants import COMPONENTS

class FlashCalculator:
    def __init__(self):
        self.pressure = 0.0
        self.temperature = 0.0
        self.composition = {comp: 0.0 for comp in COMPONENTS}

    def update_composition(self, component: str, value: float):
        if component in self.composition:
            self.composition[component] = value

    def update_pt(self, pressure: float, temperature: float):
        self.pressure = pressure
        self.temperature = temperature

    def calculate_flash(self) -> str:
        comp_str = "\n".join([f"{comp}: {val:.3f}" for comp, val in self.composition.items()])
        return (
            f"Flash calculation results:\n\n"
            f"Pressure: {self.pressure:.2f} bar\n"
            f"Temperature: {self.temperature:.2f} °C\n\n"
            f"Composition:\n{comp_str}"
        )