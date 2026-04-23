from functools import partial
from typing import Any
from .BaseEOS import EOS, EOSType
from .BrusilovskiyEOS import BrusilovskiyEOS

class EOSFactory:
    @staticmethod
    def create_eos(eos): #-> Any[EOS, partial]:
        eos_mapping = {
            # "PREOS": PREOS,
            # "SRKEOS": SRKEOS,
            "BRSEOS": BrusilovskiyEOS,
            "SRKEOS": BrusilovskiyEOS,
            "PREOS": BrusilovskiyEOS,
            # "BRSEOSV": BrusilovskiyEOSVectorTest,
            # "BRSEOSV_SRK": partial(BrusilovskiyEOSVectorTest, reduce_eos='SRK'),
            # "BRSEOSV_PR": partial(BrusilovskiyEOSVectorTest, reduce_eos='PR'),
        }
        if isinstance(eos, str):
            if eos not in eos_mapping:
                raise ValueError(f"Unknown EOS: {eos}")
            return eos_mapping[eos]
        elif issubclass(eos, EOS):
            return eos
        else:
            raise ValueError(f"Unknown EOS: {eos}")