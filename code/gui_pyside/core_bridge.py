# core_bridge.py
from PySide6.QtCore import QObject, Signal
from typing import Dict, Any, Optional, List
import sys
import os
from pathlib import Path

# Добавляем пути к вашему ядру
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from calculations.Composition.Composition import Composition
from calculations.Utils.CompositionLoader import CompositionExcelLoader


class CoreBridge(QObject):
    """Мост между UI и расчетным ядром"""
    
    # Сигналы для обновления UI
    status_update = Signal(str)
    error_occurred = Signal(str)
    result_ready = Signal(dict)
    composition_loaded = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.composition: Optional[Composition] = None
        self.composition_data: Optional[Dict] = None
        self.correlations_type = None
        self.eos_type = None
        
        # Доступные опции
        self.available_correlations = {
            'critical_temperature': ['Kesler_Lee', 'Riazi_Daubert', 'Cavett'],
            'critical_pressure': ['Riazi_Daubert', 'Lee_Kesler', 'Twu'],
            'acentric_factor': ['Edmister', 'Lee_Kesler', 'Twu'],
            'critical_volume': ['Hall_Yarborough', 'Riazi_Daubert'],
            'k_watson': ['k_watson'],
            'shift_parameter': ['Jhaveri_Youngren']
        }
        
        self.available_eos = ['PR', 'SRK']
    
    def import_composition_from_excel(self, file_path: str, sheet_name: str = 'Sheet1', has_header: bool = True) -> Dict[str, float]:
        """Импорт состава из Excel файла с использованием вашего CompositionExcelLoader"""
        self.status_update.emit(f"Импорт состава из {file_path}")
        
        try:
            # Используем ваш существующий загрузчик
            loader = CompositionExcelLoader(file_path)
            composition_dict = loader.load(header=has_header, sheet=sheet_name)
            self.status_update.emit(f'Состав словаря: {composition_dict}')

            
            self.composition = Composition(zi=composition_dict)

            self.status_update.emit('Состав создан')
            # Сохраняем данные для отображения
            self.composition_data = {
                'mole_fractions': composition_dict,
                'components': list(composition_dict.keys()),
                'has_heavy_components': len(self.composition._c6_plus_components) > 0,
                'heavy_components': self.composition._c6_plus_components
            }
            
            self.status_update.emit(f"Состав успешно импортирован. Компоненты: {len(composition_dict)}")
            self.composition_loaded.emit(self.composition_data)
            
            return composition_dict
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка импорта: {str(e)}")
            raise
    
    def set_critical_properties_correlations(self, correlations_config: Dict[str, str]):
        """Установка корреляций для критических свойств"""
        self.status_update.emit("Пересчет критических свойств с новыми корреляциями...")
        
        try:
            # Сохраняем текущий состав
            current_composition = self.composition._composition.copy()
            
            # Создаем новый объект Composition с новыми корреляциями
            self.composition = Composition(
                zi=current_composition,
                c6_plus_bips_correlation=None,
                c6_plus_correlations=correlations_config
            )
            
            self.correlations_type = correlations_config
            self.status_update.emit("Критические свойства пересчитаны")
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка расчета критических свойств: {str(e)}")
            raise
    
    def get_component_properties(self, component: str) -> Dict[str, Any]:
        """Получение свойств компонента"""
        if not self.composition:
            return {}
        
        props = {}
        for prop in ['molar_mass', 'critical_pressure', 'critical_temperature', 
                     'acentric_factor', 'critical_volume', 'shift_parameter']:
            if component in self.composition._composition_data.get(prop, {}):
                props[prop] = self.composition._composition_data[prop][component]
        
        return props
    
    def get_all_components_properties(self) -> Dict[str, Dict]:
        """Получение свойств всех компонентов"""
        if not self.composition:
            return {}
        
        properties_dict = {}
        for component in self.composition._composition.keys():
            properties_dict[component] = self.get_component_properties(component)
            properties_dict[component]['mole_fraction'] = self.composition._composition[component]
        
        return properties_dict
    
    def update_component_property(self, component: str, property_name: str, value: float):
        """Ручное изменение свойства компонента"""
        if not self.composition:
            raise ValueError("Состав не загружен")
        
        self.status_update.emit(f"Изменение {property_name} для {component} на {value}")
        
        try:
            self.composition.edit_component_properties(component, {property_name: value})
            self.status_update.emit(f"Свойство {component}.{property_name} обновлено")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка обновления свойства: {str(e)}")
            raise
    
    def update_bip(self, component_i: str, component_j: str, value: float):
        """Обновление бинарного параметра взаимодействия"""
        if not self.composition:
            raise ValueError("Состав не загружен")
        
        try:
            self.composition.edit_bip(component_i, component_j, value)
            self.status_update.emit(f"BIP ({component_i}-{component_j}) обновлен: {value}")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка обновления BIP: {str(e)}")
            raise
    
    def set_eos(self, eos_type: str):
        """Выбор уравнения состояния"""
        self.status_update.emit(f"Выбрано уравнение состояния: {eos_type}")
        self.eos_type = eos_type
        # Здесь будет инициализация вашего EOS
    
    def calculate_flash(self, pressure: float = None, temperature: float = None) -> Dict[str, Any]:
        """Выполнение flash расчета"""
        if not self.composition:
            raise ValueError("Состав не импортирован")
        
        if not self.eos_type:
            raise ValueError("Уравнение состояния не выбрано")
        
        self.status_update.emit("Выполнение flash расчета...")
        
        try:
            # TODO: Интеграция с вашим FlashCalculator
            # result = self.flash_calc.calculate(
            #     composition=self.composition,
            #     eos=self.eos_type,
            #     pressure=pressure or 101325,
            #     temperature=temperature or 298.15
            # )
            
            # Временная заглушка с реальными данными из состава
            result = {
                'type': 'Flash расчет',
                'pressure': pressure or 101325,
                'temperature': temperature or 298.15,
                'components': list(self.composition._composition.keys()),
                'mole_fractions': self.composition._composition,
                'vapor_fraction': 0.45,
                'liquid_composition': {comp: frac * 0.6 for comp, frac in self.composition._composition.items()},
                'vapor_composition': {comp: frac * 0.4 for comp, frac in self.composition._composition.items()},
            }
            
            self.result_ready.emit(result)
            self.status_update.emit("Flash расчет завершен")
            return result
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка flash расчета: {str(e)}")
            raise
    
    def calculate_pb(self, temperature: float = 298.15) -> Dict[str, Any]:
        """Расчет давления насыщения"""
        if not self.composition:
            raise ValueError("Состав не импортирован")
        
        if not self.eos_type:
            raise ValueError("Уравнение состояния не выбрано")
        
        self.status_update.emit("Расчет давления насыщения...")
        
        try:
            # TODO: Интеграция с вашим расчетом давления насыщения
            pb_value = 15e6  # Заглушка
            
            result = {
                'type': 'Давление насыщения',
                'value': pb_value,
                'value_mpa': pb_value / 1e6,
                'unit': 'Pa',
                'temperature': temperature,
                'temperature_unit': 'K'
            }
            
            self.result_ready.emit(result)
            self.status_update.emit(f"Давление насыщения: {pb_value/1e6:.2f} МПа")
            return result
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка расчета давления насыщения: {str(e)}")
            raise
    
    def has_composition(self) -> bool:
        """Проверка наличия загруженного состава"""
        return self.composition is not None
    
    def get_component_list(self) -> List[str]:
        """Получение списка компонентов"""
        if not self.composition:
            return []
        return list(self.composition._composition.keys())