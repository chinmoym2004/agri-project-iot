from flask import Flask,render_template,Response,redirect, url_for, request,jsonify

import json
import random
import time
from datetime import datetime
import ssl
import paho.mqtt.client as paho
import matplotlib.pyplot as plt
import os
from queue import Queue
import sched, time


#QUEUE FOR THE DATA 
QUEUE = Queue()

# LOAD ENV file 

from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = os.path.abspath(os.getcwd())+'/.env'
load_dotenv(dotenv_path=env_path)
# END LOAD ENV

PATH_TO_CERT = os.path.dirname(os.path.abspath(__file__))+'/console/config'
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
caPath = PATH_TO_CERT + "/" + 'AmazonRootCA1.pem'
certPath = PATH_TO_CERT + "/" + 'SS009_cert.pem'
keyPath = PATH_TO_CERT + "/" + 'SS009_private.key'
awshost=os.getenv("ENDPOINT")
awsport=int(os.getenv("MQTT_PORT"))
clientId=os.getenv("MQTT_CLIENT_ID")

# CUSTOM IMPORT
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
    #s = sched.scheduler(time.time, time.sleep)

    #def getMQTTdataFromQueue():
    queueData = QUEUE.get()
    if queueData is None:
        print("")
    else:
        return jsonify(queueData)
    #     yield f"data:{queueData}\n\n"
    # s.enter(60, 1, getMoisterDataStream,())
    
    # s.enter(60, 1, getMoisterDataStream, ())
    # s.run()

    # return Response(getMQTTdataFromQueue(), mimetype='text/event-stream')


@app.route('/moister-report/<farmid>')
def moister_report(farmid):
    #def getMoisterDataStream(farmid):
        #while True:
    json_data = json.dumps({'value': random.randint(20,35)})
    #yield f"data:{json_data}\n\n"
    #time.sleep(30)
    #s.enter(60, 1, getMoisterDataStream, (farmid,))

    return jsonify(json_data)

    #return Response(getMoisterDataStream(farmid), mimetype='text/event-stream')

@app.route('/weather-report')
def weather_report():
    lan = float(request.args.get('long'))
    lat = float(request.args.get('lat'))

    #def getWeatherDataStream(lan,lat):
        #while True:

    data = weather.get_weather_data(lat,lan)
    #print(data);
    #json_data = json.dumps({'value': random.random() * 100})
    #yield f"data:{data}\n\n"
    #time.sleep(900) #each 15 min .. we have 1000 Free call / day 
    #s.enter(60, 1, getWeatherDataStream, (lan,lat,))

    # s.enter(60, 1, getWeatherDataStream, (lan,lat,))
    # s.run()
    return jsonify(data)
    #return Response(getWeatherDataStream(lan,lat), mimetype='text/event-stream')

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
    farm_table = DataBase_Access_Model("farms")
    farms = farm_table.scan_all_items()
    return render_template('farms.html',farms=farms)

@app.route('/users')
def users():
   return render_template('users.html')


@app.route('/water-consumption')
def water_consumption():
   return render_template('water-consumption.html')


# Parse and print the payload
def message_callback(client, userdata, message):
    recv_data = json.loads(message.payload.decode('utf8').replace("'", '"'));
    json_data = json.dumps({'timestamp': recv_data['timestamp'], 'value': recv_data['value'],'device_id':recv_data['device_id']})
    print(json_data)
    QUEUE.put(json_data)
    
def on_connect(client, userdata, flags, rc):
    print("Successfully Connected to AWS cloud")
    mqttc.subscribe(MQTT_TOPIC)

if __name__ == '__main__':
    mqttc = paho.Client(client_id = clientId)               
    mqttc.on_message = message_callback
    mqttc.on_connect = on_connect        
    mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    mqttc.connect(awshost, awsport, keepalive=7200)     
    mqttc.loop_start()

    # loopCount = 0
    # scheduler = sched.scheduler(time.time, time.sleep)
    # now = time.time()

    # while True:
    #     try :
    #         # scheduler.enterabs(now+loopCount, 1, loop_func)
    #         # loopCount += 3
    #         # scheduler.run()
    #         print("In")
    #         time.sleep(2)
    #     except KeyboardInterrupt:
    #         break
    app.run(host='0.0.0.0', port=port)
