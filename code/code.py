import yaml 
with open ('code/db.yaml', 'r') as db:
    data = yaml.safe_load(db)

print(data['critical_pressure']['C1'])
print(data['acentric_factor']['C1'])