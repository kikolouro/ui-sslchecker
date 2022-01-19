from curses.ascii import SUB
import json, re, yaml, os, smtplib, ssl
from yaml.loader import SafeLoader
from pyzabbix import ZabbixAPI
from sslchecker import SSLChecker
import fnmatch
import domainexpiration
import requests
SSLChecker = SSLChecker()

def readConfig(config_file="config.yaml"):
    with open(config_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def getHosts(host="", hosts_file="data.json"):
    with open(hosts_file) as json_file:
        var = json.load(json_file)
    reg = f"*{host}*" if host != "" else "*"
    temp = {}
    #print(type(var))
    for obj in var:
        #print(obj)
        match = fnmatch.fnmatch(obj, reg)
        if match:
            temp[obj] = var[obj]
    return temp

def runchecker():
    args = getHosts()

    var = {}
    domains = {}
    var['hosts'] = []
    for host in args:
        if 'domain_only' in args[host]:
            domains[host] = args[host]
            continue
        else:
            var['hosts'].append(host)
    #print(var)
    res = SSLChecker.show_result(SSLChecker.get_args(json_args=var))

    jres = json.loads(res)
    temp = jres
    for host in list(jres):
        temp[host]['pinged'] = True
        for arg in var['hosts']:
            if arg not in jres:
                temp[arg] = {}
                temp[arg]['host'] = arg
                temp[arg]['cert_valid'] = False
                temp[arg]['pinged'] = False
    for domain in domains:
        temp[domain] = domains[domain]
    domainlist = domainexpiration.getDomains(getData('domain_only'))
    #print(domainlist)
    dnsdata = domainexpiration.domainExpiration(domainlist)

    temp = domainexpiration.mixCheckerDomain(temp, dnsdata)

    with open('data.json', 'w') as file:
        file.seek(0)
        json.dump(temp, file, indent = 4)

    return temp

def runcheckerupload(args):
    res = SSLChecker.show_result(SSLChecker.get_args(json_args=args))
    jres = json.loads(res)
    temp = jres
    for host in list(jres):
        temp[host]['pinged'] = True
        for arg in args['hosts']:
            if arg not in jres:
                temp[arg] = {'cert_valid': False, 'pinged': False}
    with open('data.json', 'w') as file:
        file.seek(0)
        json.dump(temp, file, indent = 4)
    return temp

def runsinglechecker(host):
    res = SSLChecker.show_result(SSLChecker.get_args(json_args={"hosts": [host]}))
    domainlist = domainexpiration.getDomains([host])
    dnsdata = domainexpiration.domainExpiration(domainlist)

    #print(type(res))
    res = domainexpiration.mixCheckerDomain(json.loads(res), dnsdata)
    return res

def getData(hostarg="", hosts_file="data.json"):
    with open(hosts_file) as json_file:
        hosts = json.load(json_file)
    reg = f"*{hostarg}*" if hostarg not in ["", "domain_only"] else "*"
    var = []
    for host in hosts:
        match = fnmatch.fnmatch(host, reg)
        if match:
            if hostarg != 'domain_only' and 'domain_only' in hosts[host]:
                #print(hosts[host])
                continue
            aux = {'host': host, 'cert': hosts[host]['cert_valid']}
            #print(hosts[host])
            #print(hosts[host])
            if hosts[host]['pinged'] == True:
                aux['daystoexpire'] = hosts[host]['valid_days_to_expire']
                aux['certinfo'] = f"Issued to {hosts[host]['issued_to']}"
                aux['lets'] = "Let's Encrypt" in hosts[host]['issuer_o']
                aux['wildcard'] = "*" in hosts[host]['issued_to']
            else:
                aux['daystoexpire'] = -10000
            aux['pinged'] = hosts[host]['pinged']
            if 'domain' in hosts[host]:
                aux['dns'] = hosts[host]['domain']
                aux['dns']['domain_only'] = 'domain_only' in hosts[host]
                            

            var.append(aux)
    return var

def addHosts(host, auth, zabbixhost, value, filename='data.json'):
    hostid = getZabbixHostidFromName(auth, zabbixhost)[0]['hostid']
    
    create_web_scenario(auth, host, f"https://{host}", value, hostid)
    with open(filename,'r+') as file:
        file_data = json.load(file)
        if host in file_data:
            return f'{{"error": "{host} already exists."}}'
        res = runsinglechecker(host)

        if not bool(res):
            res[host] = {}
            res[host]['host'] = host
            res[host]['cert_valid'] = False
            res[host]['pinged'] = False
        else:
            res[host]['pinged'] = True
        file_data.update(res)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
        file.seek(0)
    return "Success"

def delHost(host, filename='data.json'):
    with open(filename,'r') as file:
        file_data = json.load(file)

    if host in file_data:
        with open(filename, 'w') as file:
            file_data.pop(host, None)
            file.seek(0)
            json.dump(file_data, file, indent = 4)
    else:
        return '{"error": "Host doesn\'t exists."}'
    return "Success"


def domainValidation(domain):
    if type(domain) == str:
        regex = '^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
        return bool(re.search(regex, f"{domain}"))

def sendEmail(receiver, sender, data, port=465, smtpserver='smtp.gmail.com'):
    sender_email = sender['email']
    password = sender['password']
    already = []
    url = 'https://infosistema.webhook.office.com/webhookb2/3e386bd2-de1b-487d-b94e-f4fa057e6c1a@7f64df34-1d7b-4dce-9ca3-d683621eee67/IncomingWebhook/f7d392f0ef344a959deec314286018e7/e916be5e-b5e4-469c-a32d-47df970ecb88'
    for host in data:
        if (
            'domain' in data[host]
            and data[host]['domain']['domain'] not in already
            and data[host]['domain']['days_to_expire'] < 30
        ):
            already.append(data[host]['domain']['domain'])
            msteams = f"O Dominio está a expirar no host: {data[host]['domain']['domain']}. Expira em {data[host]['domain']['days_to_expire']} dias."
            message = f"""\
                Subject: Dominio a expirar: {data[host]['domain']['domain']}

                O Dominio está a expirar no host: {data[host]['domain']['domain']}. Expira em {data[host]['domain']['days_to_expire']} dias.""".encode('utf-8')
            SUBJECT = f"Dominio a expirar: {data[host]['domain']['domain']}"
            if data[host]['domain']['provider'] is None:
                TEXT = f"O Dominio está a expirar no host: {data[host]['domain']['domain']}. Expira em {data[host]['domain']['days_to_expire']} dias."

            else:
                TEXT = f"O Dominio está a expirar no host: {data[host]['domain']['domain']}. Expira em {data[host]['domain']['days_to_expire']} dias.\n O provider é: {data[host]['domain']['provider']}"
                msteams = f"O Dominio está a expirar no host: {data[host]['domain']['domain']}. Expira em {data[host]['domain']['days_to_expire']} dias.\n O provider é: {data[host]['domain']['provider']}"
            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
                server.login(sender_email, password)
                requests.post(url, json={"text": f"{msteams}"})
                server.sendmail(sender_email, receiver, message.encode('utf-8'))
        if data[host]['pinged'] and data[host]['valid_days_to_expire'] < 15:

            msteams = f"O certificado está a expirar no host: {host}. Expira em {data[host]['valid_days_to_expire']} dias."
            message = f"""\
                Subject: Certificado a expirar: {host}

                O certificado está a expirar no host: {host}. Expira em {data[host]['valid_days_to_expire']} dias.""".encode('utf-8')
            SUBJECT = f"Certificado a expirar: {host}"
            TEXT = f"O certificado está a expirar no host: {host}. Expira em {data[host]['valid_days_to_expire']} dias."
            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
                server.login(sender_email, password)
                requests.post(url, json={"text": f"{msteams}"})
                server.sendmail(sender_email, receiver, message.encode('utf-8'))
    return "Success"

def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def jsonfileValidation(obj):
    return 'hosts' in obj

def changeHostFile(obj, filename='data.json'):
    if jsonfileValidation(obj):
        open(filename, 'w').close()
        with open(filename, 'w') as File:
            json.dump(runcheckerupload(obj), File, indent = 4)
        filelist = list(os.listdir('temp'))
        for f in filelist:
            os.remove(os.path.join('temp', f))
        return "Success"

def getHostID(auth):
    f  = {  'host' : 'Zabbix Server'  }
    hosts = auth.host.get(filter=f, output=['hostids', 'host'] )
    #print(hosts)

def authentication(server_url, credentials):

    user = credentials['username']
    password = credentials['password']
    if server_url and user and password:
        ZABBIX_SERVER = server_url
        zapi = ZabbixAPI(ZABBIX_SERVER, user=user, password=password)
        try:
            # Login to the Zabbix API
            #zapi.login(user, password)
            #print(zapi.get_id(item_type="host", ))
            return zapi
        except Exception as e:
            print(e)
    else:
        return 'Zabbix Server url , user and password are required, try use --help'


def create_web_scenario(auth, name, url, value=500, hostid=10084, status='200,201,210-299,302'):
    hostname = ZabbixAPI.do_request(auth, 'host.get', params={"filter": {"hostid":hostid}, "output":["host"]})['result'][0]['host']
    request = ZabbixAPI.do_request(auth, 'httptest.get', params={ "filter": {"name": name}})
    if request['result']:
        return f'Host {name} already registered'
    try:
        ZabbixAPI.do_request(auth, 'httptest.create',
        params={"name": f"{name}_cenario",
        "hostid": hostid,
         "delay": '60',
         "retries": '3',
          "steps": [ { 'name': url,
           'url': url,
           'status_codes': status,
            'no': '1'} ] } )
        triggers = create_trigger(auth,name, hostname, value)
    except Exception as e:
        print(e)


def create_trigger(auth,name, host, value):

    return auth.trigger.create(
        description=f"{name} Falhou: {{ITEM.VALUE}}",
        comments="",
        expression=f"{{{host}:web.test.error[{name}_cenario].strlen()}}>0 and {{{host}:web.test.fail[{name}_cenario].last()}}>0",
        priority=5,
    )

def getScenarioID(auth, host):
    temp = ZabbixAPI.do_request(auth, 'httptest.get', params={ "filter": {"name": f"{host}_cenario"}})['result']
    return [req['httptestid'] for req in temp]


def delete_web_scenario(auth, host):
    request = getScenarioID(auth, host)
    ZabbixAPI.do_request(auth, 'httptest.delete', params=request)
    return request

def getZabbixHosts(auth):
    #print(temp)
    return ZabbixAPI.do_request(
        auth,
        'host.get',
        params={"output": ["hostid", "host"], "filter": {"status": "Enabled"}},
    )['result']

def getZabbixHostidFromName(auth, host):
    #print(temp)
    return ZabbixAPI.do_request(
        auth,
        'host.get',
        params={"output": ["hostid"], "filter": {"host": f"{host}"}},
    )['result']

def bulkImport(auth, data, zabbixhost):
    hosts = data.replace('\r', '').split('\n')
    #print(hosts)

    output = []
    for host in hosts:
        aux = {'host': host}
        if domainValidation(host):
            temp = addHosts(host, auth, zabbixhost, "10000")
            if "error" in temp:
                aux['message'] = temp
                aux['status'] = "danger"
            else:
                aux['message'] = f"{host} Adicionado com sucesso"
                aux['status'] = "success"
        else:
            aux['message'] = f"Host: {host} inválido"
            aux['status'] = "danger"
        output.append(aux)
    return output
    #print(type(data))
    