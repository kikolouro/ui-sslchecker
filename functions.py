import json, re, yaml, os, smtplib, ssl
from yaml.loader import SafeLoader
from pyzabbix import ZabbixAPI
from sslchecker import SSLChecker
import fnmatch
SSLChecker = SSLChecker()

def readConfig(config_file="config.yaml"):
    with open(config_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def getHosts(host="", hosts_file="data.json"):
    json_file = open(hosts_file)
    var = json.load(json_file)
    json_file.close()
    if host != "":
        reg = f"*{host}*"
    else:
        reg = "*"
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
    var['hosts'] = []
    for host in args:
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
                temp[arg]['cert_valid'] = False
                temp[arg]['pinged'] = False
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
                temp[arg] = {}
                temp[arg]['cert_valid'] = False
                temp[arg]['pinged'] = False
    with open('data.json', 'w') as file:
        file.seek(0)
        json.dump(temp, file, indent = 4)
    return temp

def runsinglechecker(host):
    res = SSLChecker.show_result(SSLChecker.get_args(json_args={"hosts": [host]}))
    return json.loads(res)

def getData(hostarg="", hosts_file="data.json"):
    json_file = open(hosts_file)
    hosts = json.load(json_file)
    json_file.close()
    if hostarg != "":
        reg = f"*{hostarg}*"
    else:
        reg = "*"

    var = []
    for host in hosts:
        match = fnmatch.fnmatch(host, reg)
        if match:
            aux = {}
            aux['host'] = host
            aux['cert'] = hosts[host]['cert_valid']
            if hosts[host]['pinged'] == True:
                aux['daystoexpire'] = hosts[host]['valid_days_to_expire']
            else:
                aux['daystoexpire'] = -10000
            aux['pinged'] = hosts[host]['pinged']
            var.append(aux)
    return var

def addHosts(host, auth, zabbixhost, value, filename='data.json'):
    hostid = getZabbixHostidFromName(auth, zabbixhost)[0]['hostid']
    print(hostid)
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
    regex = '^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
    if type(domain) == str:
        if re.search(regex, f"{domain}"):
            return True
        else:
            return False

def sendEmail(receiver, sender, data, port=465, smtpserver='smtp.gmail.com'):
    sender_email = sender['email']
    password = sender['password']

    for host in data:
        if data[host]['pinged']:
            if data[host]['valid_days_to_expire'] < 15:


                message = f"""\
                Subject: Certificado a expirar: {host}

                O certificado está a expirar no host: {host}. Expira em {data[host]['valid_days_to_expire']} dias.""".encode('utf-8')
                SUBJECT = f"Certificado a expirar: {host}"
                TEXT = f"O certificado está a expirar no host: {host}. Expira em {data[host]['valid_days_to_expire']} dias."
                message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
                context = ssl.create_default_context()

                with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver, message.encode('utf-8'))
    return "Success"

def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def jsonfileValidation(obj):
    if 'hosts' not in obj:
        return False
    return True

def changeHostFile(obj, filename='data.json'):
    if jsonfileValidation(obj):
        open(filename, 'w').close()
        with open(filename, 'w') as File:
            json.dump(runcheckerupload(obj), File, indent = 4)
        filelist = [ f for f in os.listdir('temp')]
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
    else:
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

    triggers = auth.trigger.create(description=f"{name} Falhou: {{ITEM.VALUE}}",
    comments="",
    expression=f"{{{host}:web.test.error[{name}_cenario].strlen()}}>0 and {{{host}:web.test.fail[{name}_cenario].last()}}>0",
    priority=5)

    triggers = auth.trigger.create(description=f"{name} está lento: {{ITEM.VALUE}}",
    comments="",
    expression=f"{{{host}:web.test.in[{name}_cenario,,bps].last()}}<{value}",
    priority=5)
    return triggers

def getScenarioID(auth, host):
    temp = ZabbixAPI.do_request(auth, 'httptest.get', params={ "filter": {"name": f"{host}_cenario"}})['result']
    request = []
    for req in temp:
        request.append(req['httptestid'])
    return request


def delete_web_scenario(auth, host):
    request = getScenarioID(auth, host)
    ZabbixAPI.do_request(auth, 'httptest.delete', params=request)
    return request

def getZabbixHosts(auth):
    temp = ZabbixAPI.do_request(auth, 'host.get', params={ "output": ["hostid", "host"], "filter":{"status": "Enabled"}})['result']
    #print(temp)
    return temp

def getZabbixHostidFromName(auth, host):
    print(host)
    temp = ZabbixAPI.do_request(auth, 'host.get', params={ "output": ["hostid"], "filter":{"host": f"{host}"}})['result']
    print(temp)
    return temp

def bulkImport(auth, data, zabbixhost):
    hosts = data.replace('\r', '').split('\n')
    #print(hosts)
    
    output = []
    for host in hosts:
        aux = {}
        aux['host'] = host
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
    