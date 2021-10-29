import time
import datetime
import ssl
import json

import paho.mqtt.client as paho
import matplotlib.pyplot as plt

PATH_TO_CERT = "..\\config"
caPath = PATH_TO_CERT + "\\" + 'AmazonRootCA1.pem'
certPath = PATH_TO_CERT + "\\" + 'SENS_2.pem.crt'
keyPath = PATH_TO_CERT + "\\" + 'SENS_2-private.pem.key'

topic = "iot/agritech"

awshost = 'ay7f3g4a6d8vz-ats.iot.us-east-1.amazonaws.com'
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
