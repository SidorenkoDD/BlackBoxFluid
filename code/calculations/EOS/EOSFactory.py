from functools import partial

from code.calculations.EOS.BaseEOS import EOS
from code.calculations.EOS.PREOS import PREOS
from code.calculations.EOS.SRKEOS import SRKEOS
from code.calculations.EOS.BrusilovskiyEOS import BrusilovskiyEOS
# from code.calculations.EOS.BRSEOS_vector import BrusilovskiyEOSVectorTest

class EOSFactory:
    @staticmethod
    def create_eos(eos_name: str) -> EOS:
        eos_mapping = {
            "PREOS": PREOS,
            "SRKEOS": SRKEOS,
            "BRSEOS": BrusilovskiyEOS,
            "BRSEOS_SRK": partial(BrusilovskiyEOS, reduce_eos='SRK'),
            "BRSEOS_PR": partial(BrusilovskiyEOS, reduce_eos='PR'),
        }
        if eos_name not in eos_mapping:
            raise ValueError(f"Unknown EOS: {eos_name}")
        return eos_mapping[eos_name]