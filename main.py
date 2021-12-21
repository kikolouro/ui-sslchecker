from re import T
from flask import Flask, request, render_template, send_from_directory, redirect
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
import functions
import os, json, urllib
import ast
import domainexpiration
app = Flask(__name__, template_folder='html')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, './temp')
ALLOWED_EXTENSIONS = {'json'}
app.config.update(TEMPLATES_AUTO_RELOAD = True)
yaml = functions.readConfig()
configapp = yaml['app']
configzabbix = yaml['zabbix']
configemail = yaml['email']
app.config['DEBUG'] = True
zabbixauth = functions.authentication(configzabbix['server'], configzabbix['credentials'])
if configapp['env'] != 'dev':
    app.config['DEBUG'] = True
    app.config['BASIC_AUTH_USERNAME'] = configapp['credentials']['username']
    app.config['BASIC_AUTH_PASSWORD'] = configapp['credentials']['password']
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app)

@app.route("/api/v1/uploadhosts", methods=['POST'])
def upload():
    data = request.form['data']
    hostid = request.form['hostid']
    if len(data) == 0:
        return "Erro: Não pode ficar vazio" 
    message = functions.bulkImport(zabbixauth, data, hostid)
    #print(json.dumps(message))
    #request.form.add('message', message)
    
    return redirect(f'/?message={urllib.parse.quote(str(message))}', code=307)

@app.route("/api/v1/runchecker", methods=['POST'])
def runchecker():
    return functions.runchecker()

@app.route('/api/v1/sendemail', methods=['POST'])
def sendemail():
    data = request.json
    return functions.sendEmail(configemail['receiver'], configemail['sender'], data)

@app.route("/api/v1/addhost", methods=['GET', 'POST'])
def addHost():
    host = request.form['host']
    hostid = request.form['hostid']
    value = request.form['bps']
    #print(value)
    if functions.domainValidation(host):
        temp = functions.addHosts(host, zabbixauth, hostid, value)
        if "error" in temp:
            return f"{temp}"
        else:
            return "Success"
    else:
        return "Wrong domain format"

@app.route("/api/v1/adddomain", methods=['GET', 'POST'])
def addDomain():
    domain = request.form['domain']
    if not functions.domainValidation(domain):
        return "Wrong domain format"
    temp = domainexpiration.addDomain(domain)
    if "error" in temp:
        return f"{temp}"
    else:
        return "Success"
# TO BE WORKED
@app.route("/v1/api/gethostfile")
def gethostfile():
    uploads = os.path.join(app.root_path, './temp')
    with open('temp/hosts.json', 'w') as file:
        temp = {'hosts': []}
        data = functions.getData()
        for host in data:
            temp['hosts'].append(host)
        json.dump(temp, file, indent = 4)
        file.seek(0)
        return send_from_directory(uploads, 'hosts.json', as_attachment=True)

@app.route("/api/v1/gethosts")
def getHosts():
    host = request.args.get('host')
    if host is None:
        return functions.getHosts()
    else:
        return functions.getHosts(host)

@app.route("/api/v1/getdata")
def getData():
    host = request.args.get('host')
    if host is None:
        return functions.getData()
    else:
        return functions.getData(host)

@app.route("/api/v1/delhost", methods=['POST'])
def delHost():
    host = request.form['host']
    if not functions.domainValidation(host):
        return "Wrong domain format"
    temp = functions.delHost(host)
    functions.delete_web_scenario(zabbixauth, host)
    if "error" in temp:
        return f"{temp}"
    else:
        return "Success"


@app.route("/api/v1/deldomain", methods=['POST'])
def delDomain():
    host = request.form['host']
    if not functions.domainValidation(host):
        return "Wrong domain format"
    temp = domainexpiration.delDomain(host)
    if "error" in temp:
        return f"{temp}"
    else:
        return "Success"

@app.route("/", methods=['GET', 'POST'])
def root():
    data = functions.getData()
    zabbixdata = functions.getZabbixHosts(zabbixauth)
    data.sort(key = lambda x:x["daystoexpire"])

    if request.args.get('message') is None:
        return render_template('index.html', data = data, zabbixdata=zabbixdata)
    message = request.args.get('message')
    #message = urllib.parse.unquote(request.args.get('message'))
    e = ast.literal_eval(message)
    #print(e[0])
    return render_template('index.html', data = data, zabbixdata=zabbixdata, message=e)
    

@app.route("/newhosts")
def newhost():
    data = functions.getZabbixHosts(zabbixauth)
    return render_template('newhosts.html', data = data)

@app.route("/debugging")
def debugging():
    return render_template("debugging.html")

@app.route("/domains")
def domains():
    data = functions.getData('domain_only')
    zabbixdata = functions.getZabbixHosts(zabbixauth)
    data.sort(key = lambda x:x["daystoexpire"])
    data = domainexpiration.getDomaindata(data)
    data.sort(key = lambda x:x["days_to_expire"])
    return render_template("domains.html", data=data)