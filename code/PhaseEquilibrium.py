class PhaseEquilibrium:

    def __init__(self, zi : dict):
        self.zi = zi

        if sum(zi.values()) != 100:
            raise ValueError('Сумма компонентов не равна 100')
        else:
            print('Сумма компонентов равна 100')
        

if __name__ == '__main__':
    pe = PhaseEquilibrium({'C1': 25, 'C2': 25, 'C3':50})
    