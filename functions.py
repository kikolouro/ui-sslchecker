import json, re, yaml
from yaml.loader import SafeLoader

def readConfig(config_file="config.yaml"):
    with open(config_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def getHosts(hosts_file="hosts.json"):
    json_file = open(hosts_file)
    var = json.load(json_file)
    json_file.close()
    return var

def addHosts(host, filename='hosts.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        if host in file_data['hosts']:
            return '{"error": "Host already exists."}'
        file_data["hosts"].append(host)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
    return "Success" 

def delHost(host, filename='hosts.json'):
    with open(filename,'r') as file:
        file_data = json.load(file)
    if host in file_data['hosts']:
        with open(filename, 'w') as file:
            i = file_data['hosts'].index(host)
            file_data['hosts'].pop(i)
            file.seek(0)
            json.dump(file_data, file, indent = 4)
    else:
        return '{"error": "Host doesn\'t exists."}'
    return "Success"
        

def domainValidation(domain):
    regex = '^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
    if type(domain) == str:
        if re.search(regex, f"{domain}"):
            return True
        else:
            return False

