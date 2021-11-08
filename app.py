from flask import Flask,render_template,Response,redirect, url_for, request

import json
import random
import time
from datetime import datetime
import ssl
import paho.mqtt.client as paho
import matplotlib.pyplot as plt
import os
from queue import Queue

#QUEUE FOR THE DATA 
QUEUE = Queue()

# LOAD ENV file 

from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = os.path.abspath(os.getcwd())+'/.env'
load_dotenv(dotenv_path=env_path)
# END LOAD ENV

# CUSTOM IMPORT
import awsconfig
import weather
from console.src.database import DataBase_Access_Model

port = os.getenv("APP_PORT")

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    # soilss = [
    #     {
    #         'device_id' : 'SENS_01',
    #         'label' : 'SS 1',
    #         'status' : 1
    #     },
    #     {
    #         'device_id': 'SENS_2',
    #         'label' : 'SS 2',
    #         'status' : 1
    #     },
    #     {
    #         'device_id': 'SENS_3',
    #         'label' : 'SS 3',
    #         'status' : 1
    #     },
    #     {
    #         'device_id': 'SENS_4',
    #         'label' : 'SS 4',
    #         'status' : 1
    #     }
    # ]

    device_table = DataBase_Access_Model("devices")
    soilss = device_table.get_by_condition('device_type','ss')


    #scan_all_items
    farm_table = DataBase_Access_Model("farms")
    # farms = [
    #     {
    #         'farm_id' : 'F001',
    #         'label' : 'Farm 1',
    #         'long':'78.3407965',
    #         'lat': '17.4628965'
    #     },
    #     {
    #         'farm_id': 'F002',
    #         'label' : 'Farm 2',
    #         'long':'80.138236',
    #         'lat':'12.9298971'
    #     },
    #     {
    #         'farm_id': 'F003',
    #         'label' : 'Farm 3',
    #         'long':'87.5679722',
    #         'lat': '22.7224444'
    #     },
    #     {
    #         'farm_id': 'F004',
    #         'label' : 'Farm 4',
    #         'long':'77.9467335',
    #         'lat': '10.2087529'
    #     }
    # ]
    farms = farm_table.scan_all_items()


    return render_template('index.html',soilss=soilss,farms=farms)


@app.route('/chart-data')
def chart_data():
    def getMQTTdataFromQueue():
        while True:
            queueData = QUEUE.get()
            print("Data in QUEUE");
            print(queueData)

            if queueData is None:
                time.sleep(1)
                continue

            # for x in queueData:
            #     print(x)
            #     parse_data = json.dumps({'time': x.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'value':x.value})
            
            yield f"data:{queueData}\n\n"

            # json_data = json.dumps(
            #     {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
           

        # while True:
        #     json_data = json.dumps(
        #         {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
        #     yield f"data:{json_data}\n\n"
        #     time.sleep(1)
    return Response(getMQTTdataFromQueue(), mimetype='text/event-stream')


@app.route('/moister-report/<farmid>')
def moister_report(farmid):
    def getMoisterDataStream(farmid):
        while True:
            json_data = json.dumps({'value': random.randint(20,50)})
            yield f"data:{json_data}\n\n"
            time.sleep(30)
    return Response(getMoisterDataStream(farmid), mimetype='text/event-stream')

@app.route('/weather-report')
def weather_report():
    lan = float(request.args.get('long'))
    lat = float(request.args.get('lat'))
    def getWeatherDataStream(lan,lat):
        while True:
            data = weather.get_weather_data(lat,lan)
            print(data);
            #json_data = json.dumps({'value': random.random() * 100})
            yield f"data:{data}\n\n"
            time.sleep(900) #each 15 min .. we have 1000 Free call / day 

    return Response(getWeatherDataStream(lan,lat), mimetype='text/event-stream')

@app.route('/soilsensors')
def soilsensors():
    device_table = DataBase_Access_Model("devices")
    soilss = device_table.get_by_condition('device_type','ss')
    return render_template('soilsensors.html',soilss=soilss)

@app.route('/sprinklers')
def sprinklers():
    device_table = DataBase_Access_Model("devices")
    sps = device_table.get_by_condition('device_type','sp')
    return render_template('sprinklers.html',sps=sps)

@app.route('/farms')
def farms():
   return render_template('farms.html')

@app.route('/users')
def users():
   return render_template('users.html')


# Parse and print the payload
def message_callback(client, userdata, message):
    recv_data = json.loads(message.payload.decode('utf8').replace("'", '"'));
    json_data = json.dumps({'timestamp': recv_data['timestamp'], 'value': recv_data['value'],'deviceid':recv_data['deviceid']})
    QUEUE.put(json_data)
    
def on_connect(client, userdata, flags, rc):
    print("Successfully Connected to AWS cloud")
    mqttc.subscribe(awsconfig.topic)

if __name__ == '__main__':
    mqttc = paho.Client(client_id = awsconfig.clientId)               
    mqttc.on_message = message_callback
    mqttc.on_connect = on_connect        
    mqttc.tls_set(awsconfig.caPath, certfile=awsconfig.certPath, keyfile=awsconfig.keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    mqttc.connect(awsconfig.awshost, awsconfig.awsport, keepalive=60)     
    mqttc.loop_start()
    app.run(host='0.0.0.0', port=port)
