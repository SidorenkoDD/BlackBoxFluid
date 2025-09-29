from calculations.EOS.BaseEOS import EOS

class EOSRootChooser:
    def __init__(self, eos_obj:EOS):
        self._eos_obj = eos_obj
        

    def define_root_for_phase(self,phase: str):
        if phase == 'liquid':
            self._eos_obj._z = min(filter(lambda x: x>0, self._eos_obj.real_roots_eos))
        elif phase == 'vapour':
            self._eos_obj._z = max(self._eos_obj.real_roots_eos)
        else:
            raise ValueError(f'No phase {phase} for EOSRootChooser')
