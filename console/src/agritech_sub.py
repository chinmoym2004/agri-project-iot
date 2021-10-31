import time
import datetime
import ssl
import json

# LOAD ENV file 
import os
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = os.path.abspath(os.getcwd())+'/.env'
load_dotenv(dotenv_path=env_path)

# END LOAD ENV

import paho.mqtt.client as paho
import matplotlib.pyplot as plt

PATH_TO_CERT = os.path.dirname(os.path.abspath(__file__))+'/../config'

caPath = PATH_TO_CERT + "/" + 'AmazonRootCA1.pem'
certPath = PATH_TO_CERT + "/" + 'SENS_2.pem.crt'
keyPath = PATH_TO_CERT + "/" + 'SENS_2-private.pem.key'

topic = "iot/agritech"

awshost = os.getenv("ENDPOINT")
awsport = 8883
clientId = 'agritech_1'
thingName = 'debug_1'


# Parse and print the payload
def message_callback(client, userdata, message):
    recv_data = message.payload;
    print(recv_data)
    
def on_connect(client, userdata, flags, rc):
    print("Successfully Connected to AWS cloud")
    mqttc.subscribe(topic) 

# Main routine       
if __name__ == '__main__':
    
    mqttc = paho.Client(client_id = clientId)               
    mqttc.on_message = message_callback
    mqttc.on_connect = on_connect        
    mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    mqttc.connect(awshost, awsport, keepalive=60)     
    mqttc.loop_start()   
    
    while(True):
        pass
