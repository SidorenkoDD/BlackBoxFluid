'''
module to import composition and create dict
'''
from abc import ABC, abstractmethod
from calculations.Utils.Errors import InvalidExcelComponentType, InvalidExcelValueType
import pandas as pd

class CompositionLoader(ABC):
    def __init__(self, filepath):
        self._filepath = filepath
        self.load()
    @abstractmethod
    def load(self):
        pass


class CompositionExcelLoader(CompositionLoader):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.load()

    def load(self):
        ##TODO: может быть ошибка, если header есть, а предполагается, что его нет
        df = pd.read_excel(io = self._filepath,
                           header = None)

        df.columns = ["key", "value"]

        if not pd.api.types.is_numeric_dtype(df['value']):
            raise InvalidExcelValueType('Value not numeric in Excel!')

        if not pd.api.types.is_string_dtype(df['key']):
            raise InvalidExcelComponentType('Value not string in Excel!')

        dict_from_df = df.set_index('key')['value'].to_dict()
        return dict_from_df