import json


class DBReader:
    def __init__(self):
        pass

    def get_all_acentric_factor_labels(self):
        with open('code/db/acentric_factor.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    


    def get_all_bips_labels(self):
        with open('code/db/bips.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    


    def get_all_molar_mass_labels(self):
        with open('code/db/molar_mass.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    


    def get_all_pcrit_labels(self):
        with open('code/db/pcrit.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    


    def get_all_tcrit_labels(self):
        with open('code/db/tcrit.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    


    def get_all_shift_labels(self):
        with open('code/db/shift.json', 'r') as f:
            self.data = json.load(f)

        return list(self.data.keys())
    

if __name__ == '__main__':
    dbreader = DBReader()
    #print(dbreader.get_all_bips_labels())
    print(dbreader.get_all_acentric_factor_labels())
    print(dbreader.get_all_molar_mass_labels())
    print(dbreader.get_all_pcrit_labels())
    print(dbreader.get_all_tcrit_labels())
    print(dbreader.get_all_shift_labels())