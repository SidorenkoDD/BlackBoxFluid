from abc import ABC, abstractmethod
import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from calculations.Composition.Composition import Composition
from calculations.CompositionalModel.CompositionalModel import CompositionalModel

# class ExportFacade:
#     def __init__(self):
#         self.E300 = E300()

class Export(ABC):
    @abstractmethod
    def export(self):
        ...


class E300(Export):
    def __init__(self, model: CompositionalModel):
        self._model = model

    def _write_eos(self, fname):
        fname.write('EOS\n')
        fname.write('--\n')
        fname.write('--Equation of state\n')
        fname.write('--\n')
        fname.write(f'{self._model._eos}\n')
        fname.write('/\n')


    def _write_n_comps(self, fname):
        fname.write('NCOMPS\n')
        fname.write('--\n')
        fname.write('--Number of components\n')
        fname.write('--\n')
        fname.write(f'{len(self._model._composition._composition.keys())}\n')
        fname.write('/\n')

    def _write_comps(self, fname):
        fname.write('CNAMES\n')
        fname.write('--\n')
        fname.write('--Component Names\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{component}\n')
        fname.write('/\n')

    def _write_mw(self, fname):
        fname.write('MW\n')
        fname.write('--\n')
        fname.write('--Molecular Weight\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{self._model._composition._composition_data['molar_mass'][component]}\n')
        fname.write('/\n')

    def _write_tc(self, fname):
        fname.write('TCRIT\n')
        fname.write('--\n')
        fname.write('--Critical Temperature\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{self._model._composition._composition_data['critical_temperature'][component]}\n')
        fname.write('/\n')

    def _write_pc(self, fname):
        fname.write('PCRIT\n')
        fname.write('--\n')
        fname.write('--Critical Pressure\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{self._model._composition._composition_data['critical_pressure'][component]}\n')
        fname.write('/\n')

    def _write_vc(self, fname):
        fname.write('VCRIT\n')
        fname.write('--\n')
        fname.write('--Critical Volume\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{self._model._composition._composition_data['critical_volume'][component]}\n')
        fname.write('/\n')

    def _write_acf(self, fname):
        fname.write('ACF\n')
        fname.write('--\n')
        fname.write('--Acentric factors\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{self._model._composition._composition_data['acentric_factor'][component]}\n')
        fname.write('/\n')


    def _write_shift(self, fname):
        fname.write('SSHIFT\n')
        fname.write('--\n')
        fname.write('--Eos Volume Shift\n')
        fname.write('--\n')
        for component in list(self._model._composition._composition.keys()):
            fname.write(f'{self._model._composition._composition_data['shift_parameter'][component]}\n')
        fname.write('/\n')

    def _write_info(self, fname):
        fname.write('-- Auto generated file with python\n')


    def export(self, fname:str):
        with open(f'{fname}.inc', 'w') as result_file:
            result_file.write('--E300.inc\n')
            self._write_info(result_file)
            self._write_eos(result_file)
            self._write_n_comps(result_file)
            self._write_comps(result_file)
            self._write_mw(result_file)
            self._write_tc(result_file)
            self._write_pc(result_file)
            self._write_vc(result_file)
            self._write_acf(result_file)
            self._write_shift(result_file)





if __name__ == '__main__':
    comp = Composition({'C1':0.5, 'C2':0.5})
    model = CompositionalModel(comp)
    e300_exporter = E300(model)
    e300_exporter.export('first')