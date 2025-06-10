class PhaseEquilibrium:
    
    '''
    Алгоритм

    1. Ввод zi, Р и Т
    2. Решаем УРС для состава zi
        2.1. Выбираем Z
        2.2. Расчет f
    3. Расчет начальные Кi
    4. Расчет yi_v и xi_l
    5. Решаем УРС для yi_v и xi_l
    6. Выбираем Zy и Zl
    7. Расчет f для каждой фазы
    8. Расчет Ri_v Ri_l
    9. Проверка сходимости -> Обновление Ki
    
    '''
    def __init__(self, zi : dict):
        self.zi = zi

        if sum(zi.values()) != 100:
            raise ValueError('Сумма компонентов не равна 100')
        else:
            print('Сумма компонентов равна 100')
        
    def calc_flash():
        pass


if __name__ == '__main__':
    pe = PhaseEquilibrium({'C1': 25, 'C2': 25, 'C3':50})
    