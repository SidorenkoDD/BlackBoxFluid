class Conditions:
    '''
    Класс для хранения термобарических условий
    '''
    def __init__(self, p, t):
        self.p = p
        self.t = t + 273.14