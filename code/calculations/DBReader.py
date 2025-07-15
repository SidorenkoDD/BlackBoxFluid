import yaml

class DBReader:
    def __init__(self):
        with open('code/calculations/db.yaml') as yaml_file:
            self.db = yaml.safe_load(yaml_file)

    
    def get_keys(self):
        return self.db.keys()
    
    def get_data(self, x):
        return self.db[x]
    

if __name__ == '__main__':
    dbreader = DBReader()
    print(dbreader.get_keys())
    print(dbreader.get_data('molar_mass'))