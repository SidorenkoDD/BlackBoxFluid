from InterfaceEOS import EOS
from PREOS import PREOS
from SRKEOS_MOCK import SRKEOS

class EOSFactory:
    @staticmethod
    def create_eos(eos_name: str) -> EOS:
        eos_mapping = {
            "PREOS": PREOS,
            "SRKEOS": SRKEOS,
        }
        if eos_name not in eos_mapping:
            raise ValueError(f"Unknown EOS: {eos_name}")
        return eos_mapping[eos_name]