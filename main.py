from re import T
from flask import Flask, request, render_template, send_from_directory, redirect
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
import functions
import os, json
app = Flask(__name__, template_folder='html')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, './temp')
ALLOWED_EXTENSIONS = {'json'}
app.config.update(TEMPLATES_AUTO_RELOAD = True)
yaml = functions.readConfig()
configapp = yaml['app']
configzabbix = yaml['zabbix']
configemail = yaml['email']

zabbixauth = functions.authentication(configzabbix['server'], configzabbix['credentials'])
if configapp['env'] != 'dev':
    app.config['DEBUG'] = True
    app.config['BASIC_AUTH_USERNAME'] = configapp['credentials']['username']
    app.config['BASIC_AUTH_PASSWORD'] = configapp['credentials']['password']
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app)

@app.route("/api/v1/uploadhosts", methods=['POST'])
def upload():
    if 'file' not in request.files:
        return '{"error":"Nenhum ficheiro enviado."}'
    file = request.files['file']
    if file.filename == '':
        return '{"error":"Nenhum ficheiro enviado."}'
    if file and functions.allowed_file(file.filename, ALLOWED_EXTENSIONS):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(f"{app.config['UPLOAD_FOLDER']}/{filename}", "r") as File:
            var = json.load(File)
            functions.changeHostFile(var)
        """with open('data.json', 'r+') as File:
            res = functions.runchecker()
            file_data = json.load(File)
            file_data.update(res)
            
            File.seek(0)
            json.dump(file_data, File, indent = 4)"""
    return redirect("/")

@app.route("/api/v1/runchecker", methods=['POST'])
def runchecker():
    return functions.runchecker()

@app.route('/api/v1/sendemail', methods=['POST'])
def sendemail():
    data = request.json
    return functions.sendEmail(configemail['receiver'], configemail['sender'], data)

@app.route("/api/v1/addhost", methods=['POST'])
def addHost():
    host = request.form['host']
    hostid = request.form['hostid']
    if functions.domainValidation(host):
        temp = functions.addHosts(host, zabbixauth, hostid)
        if "error" in temp:
            return f"{temp}"
        else:
            return "Success"
    else:
        return "Wrong domain format"
# TO BE WORKED
@app.route("/v1/api/gethostfile")
def gethostfile():
    uploads = os.path.join(app.root_path, './temp')
    with open('temp/hosts.json', 'w') as file:
        temp = {}
        temp['hosts'] = []
        data = functions.getData()
        for host in data:
            temp['hosts'].append(host)
        json.dump(temp, file, indent = 4)
        file.seek(0)
        return send_from_directory(uploads, 'hosts.json', as_attachment=True)

@app.route("/api/v1/gethosts")
def getHosts():
    host = request.args.get('host')
    if host == None:
        return functions.getHosts()
    else:
        return functions.getHosts(host)

@app.route("/api/v1/getdata")
def getData():
    host = request.args.get('host')
    if host == None:
        return functions.getData()
    else:
        return functions.getData(host)

@app.route("/api/v1/delhost", methods=['POST'])
def delHost():
    host = request.form['host']
    if functions.domainValidation(host):
        temp = functions.delHost(host)
        functions.delete_web_scenario(zabbixauth, host)
        if "error" in temp:
            return f"{temp}"
        else:
            return "Success"
    else:
        return "Wrong domain format"


@app.route("/")
def root():
    data = functions.getData()

    data.sort(key = lambda x:x["daystoexpire"])
    

    return render_template('index.html', data = data)

@app.route("/newhosts")
def newhost():
    data = functions.getZabbixHosts(zabbixauth)
    return render_template('newhosts.html', data = data)

@app.route("/debugging")
def debugging():
    return render_template("debugging.html")

