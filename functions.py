import json, re, yaml, os, smtplib, ssl
from yaml.loader import SafeLoader
from pyzabbix import ZabbixAPI
from sslchecker import SSLChecker

SSLChecker = SSLChecker()

def readConfig(config_file="config.yaml"):
    with open(config_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data


def getHosts(hosts_file="hosts.json"):
    json_file = open(hosts_file)
    var = json.load(json_file)
    json_file.close()
    return var

def runchecker():
    args = getHosts()
    res = SSLChecker.show_result(SSLChecker.get_args(json_args=args))
    return json.loads(res)

def runsinglechecker(host):
    res = SSLChecker.show_result(SSLChecker.get_args(json_args={"hosts": [host], "verbose":True}))
    return json.loads(res)

def getData(hosts_file="data.json"):
    json_file = open(hosts_file)
    hosts = json.load(json_file)
    json_file.close()
    var = {}
    for host in hosts:
        var[host] = {}
        var[f'{host}']['cert'] = hosts[host]['cert_valid']
        var[host]['daystoexpire'] = hosts[host]['valid_days_to_expire']
    return var

def addHosts(host, auth, filename='hosts.json'):
    #create_web_scenario(auth, host, f"https://{host}")
    with open(filename,'r+') as file:
        file_data = json.load(file)
        if host in file_data['hosts']:
            return '{"error": "Host already exists."}'
        file_data["hosts"].append(host)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
        file.seek(0)
    
    with open('data.json', 'r+') as File:
        res = runsinglechecker(host)
        print(res)
        file_data = json.load(File)
        print(file_data)
        json.dump(file_data, File, indent = 4)
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

def sendEmail(receiver, sender, host, daysleft, port=465, smtpserver='smtp.gmail.com'):
    sender_email = sender['email']
    password = sender['password']

    message = f"""\
    Certificado a expirar: {host}

    O certificado está a expirar no host: {host}. Expira em {daysleft} dias.""".encode('utf-8')
   
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver, message)
        return "Success"

def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def jsonfileValidation(obj):
    if 'hosts' not in obj:
        return False
    return True

def changeHostFile(obj, filename='hosts.json'):
    if jsonfileValidation(obj):
        open(filename, 'w').close()
        with open(filename, 'w') as File:
            json.dump(obj, File, indent = 4)
        filelist = [ f for f in os.listdir('temp')]
        for f in filelist:
            os.remove(os.path.join('temp', f))
        return "Success"

def getHostID(auth):
    f  = {  'host' : 'Zabbix Server'  }
    hosts = auth.host.get(filter=f, output=['hostids', 'host'] )
    print(hosts)

def authentication(server_url, credentials):

    user = credentials['username']
    password = credentials['password']
    if server_url and user and password:
        ZABBIX_SERVER = server_url
        zapi = ZabbixAPI(ZABBIX_SERVER, user=user, password=password)
        try:
            # Login to the Zabbix API
            #zapi.login(user, password)
            print(zapi.get_id(item_type="host", ))
            return zapi
        except Exception as e:
            print(e)
    else:
        return 'Zabbix Server url , user and password are required, try use --help'


def create_web_scenario(auth, name, url, hostid=10084, status='200,201,210-299,302'):
    
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
            triggers = create_trigger(auth,name)
        except Exception as e:
            print(e)


def create_trigger(auth,name):
    
    triggers = auth.trigger.create(description=f"{name} Falhou: {{ITEM.VALUE}}",
    comments="",
    expression=f"{{Zabbix server:web.test.error[{name}_cenario].strlen()}}>0 and {{Zabbix server:web.test.fail[{name}_cenario].last()}}>0",
    priority=5)

    triggers = auth.trigger.create(description=f"{name} está lento: {{ITEM.VALUE}}",
    comments="",
    expression=f"{{Zabbix server:web.test.in[{name}_cenario,,bps].last()}}<500",
    priority=5)
    return triggers
