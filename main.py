from sslchecker import SSLChecker
from flask import Flask, request, render_template, send_from_directory
from flask_basicauth import BasicAuth
import functions
app = Flask(__name__, template_folder='static')
app.config.update(TEMPLATES_AUTO_RELOAD = True)

yaml = functions.readConfig()
configapp = yaml['app']
configzabbix = yaml['zabbix']
configemail = yaml['email']

if configapp['env'] != 'dev':
    app.config['BASIC_AUTH_USERNAME'] = configapp['credentials']['username']
    app.config['BASIC_AUTH_PASSWORD'] = configapp['credentials']['password']
    app.config['BASIC_AUTH_FORCE'] = True
    basic_auth = BasicAuth(app)


@app.route("/api/v1/runchecker", methods=['POST'])
def runchecker():
    args = functions.getHosts()
    res = SSLChecker.show_result(SSLChecker.get_args(json_args=args))
    return res

@app.route('/api/v1/sendemail', methods=['POST'])
def sendemail():
    return functions.sendEmail(configemail['receiver'], configemail['sender'], 'example.com', 30)

@app.route("/api/v1/addhost", methods=['POST'])
def addHost():
    host = request.form['host']
    if functions.domainValidation(host):
        temp = functions.addHosts(host)
        if "error" in temp:
            return f"{temp}"
        else:
            return "Success"
    else:
        return "Wrong domain format"

@app.route("/api/v1/delhost", methods=['POST'])
def delHost():
    host = request.form['host']
    if functions.domainValidation(host):
        temp = functions.delHost(host)
        if "error" in temp:
            return f"{temp}"
        else:
            return "Success"
    else:
        return "Wrong domain format"

@app.route("/")
def root():
    
    return render_template('index.html')

SSLChecker = SSLChecker()
