import whois
from datetime import datetime
import json
import re
import functions
now = datetime.now()

def getDomains(data):
    temp = []
    #print(host['host'])
    regex = '([a-z0-9\-]+)\.([a-z]+|[a-z]{2}\.[a-z]+)$'
    for host in data:
        r = re.compile(regex)
        #print(host)
        aux = r.search(f"{host['host']}") if len(data) > 1 else r.search(f"{host}")
        temp.append(f"{aux.group(1)}.{aux.group(2)}")

    res = []
    for i in temp:
        if i not in res:
            res.append(i)
    #print(res)
    return res

def getsingleDomain(data):
    temp = []
    #print(host['host'])
    regex = '([a-z0-9\-]+)\.([a-z]+|[a-z]{2}\.[a-z]+)$'
    r = re.compile(regex)
    aux = r.search(f"{data}")
    temp.append(f"{aux.group(1)}.{aux.group(2)}")

    return temp

def domainExpiration(domainlist):
    
    res = []
    for domain in domainlist:
        try:
            temp = {}
            w = whois.whois(domain)
            if w.domain_name is None:
                temp['domain'] = domain
                temp['days_to_expire'] = 200000
                temp['domain_expiration_date'] = None
                temp['provider'] = None
            else:
                if type(w.expiration_date) != list:        
                    domain_expiration_date = str(w.expiration_date.day) + '/' + str(w.expiration_date.month) + '/' + str(w.expiration_date.year)
                    timedelta = w.expiration_date - now
                else:
                    domain_expiration_date = str(min(w.expiration_date).day) + '/' + str(min(w.expiration_date).month) + '/' + str(min(w.expiration_date).year)
                    #print("LIST")
                days_to_expire = timedelta.days

                temp['domain'] = domain
                temp['days_to_expire'] = days_to_expire
                temp['domain_expiration_date'] = domain_expiration_date
                temp['provider'] = w.whois_server
            res.append(json.dumps(temp))
        except Exception as e:
            continue
    return res

def addDomain(domain, filename='data.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        if domain in file_data:
            return f'{{"error": "{domain} already exists."}}'
        
        res = file_data
        temp = domainExpiration([f'{domain}'])
        res[domain] = {}
        res[domain]['host'] = domain
        res[domain]['domain_only'] = True
        res[domain]['cert_valid'] = False
        res[domain]['valid_days_to_expire'] = 200000
        res[domain]['pinged'] = False
        res[domain]['domain'] = json.loads(temp[0])

        file_data.update(res)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
        file.seek(0)
    return "Success"

def delDomain(domain, filename='data.json'):
    with open(filename,'r') as file:
        file_data = json.load(file)

    if domain in file_data:
        with open(filename, 'w') as file:
            file_data.pop(domain, None)
            file.seek(0)
            json.dump(file_data, file, indent = 4)
    else:
        return '{"error": "Host doesn\'t exists."}'
    return "Success"


def mixCheckerDomain(checker, domain):
    temp = {}
    already = []
    #print(checker)
    for host in checker:
        #print(host)
        host = checker[host]
        temp[host['host']] = host
        for dns in domain:
            dns = json.loads(dns)
            if dns['domain'] not in already and dns['domain'] in host['host']:
                temp[host['host']]['domain'] = dns
                already.append(host['host'])
    return temp


def getDomaindata(data):
    temp = []
    already = []
    for host in data:
        if (
            'domain' in json.dumps(host)
            and host['dns']['domain'] not in already
        ):
            if 'domain_only' in host:
                host['dns']['domain_only'] = True
            #print(host)
            temp.append(host['dns'])
            already.append(host['dns']['domain'])
    return temp