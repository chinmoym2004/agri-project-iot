import time
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import random
import datetime
import sched

# LOAD ENV file 
import os
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = os.path.abspath(os.getcwd())+'/.env'
load_dotenv(dotenv_path=env_path)

# END LOAD ENV


# Define ENDPOINT, TOPIC, RELATOVE DIRECTORY for CERTIFICATE AND KEYS
ENDPOINT = os.getenv("ENDPOINT")
PATH_TO_CERT = os.path.dirname(os.path.abspath(__file__))+'/../config'

TOPIC = "iot/agritech"

# AWS class to create number of objects (devices)
class AWS():
    # Constructor that accepts client id that works as device id and file names for different devices
    # This method will obviosuly be called while creating the instance
    # It will create the MQTT client for AWS using the credentials
    # Connect operation will make sure that connection is established between the device and AWS MQTT
    def __init__(self, client, certificate, private_key):
        self.client_id = client
        self.device_id = client
        self.cert_path = PATH_TO_CERT + "/" + certificate
        self.pvt_key_path = PATH_TO_CERT + "/" + private_key
        self.root_path = PATH_TO_CERT + "/" + "AmazonRootCA1.pem"
        self.myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.root_path, self.pvt_key_path, self.cert_path)
        self._connect()

    # Connect method to establish connection with AWS IoT core MQTT
    def _connect(self):
        self.myAWSIoTMQTTClient.connect()

    # This method will publish the data on MQTT 
    # Before publishing we are confiuguring message to be published on MQTT
    def publish(self):
        #print('Begin Publish')
        #if loopcount % 300 == 0:
        try:
            message = {}    
            value = float(random.normalvariate(28, 4))
            value = round(value, 1)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message['deviceid'] = self.device_id
            message['timestamp'] = timestamp
            message['datatype'] = 'Soil Moisture'
            message['value'] = value
            messageJson = json.dumps(message)
            self.myAWSIoTMQTTClient.publish(TOPIC, messageJson, 1) 
            print("Published: '" + json.dumps(message) + "' to the topic: " + TOPIC)
            time.sleep(0.1)
        except publishTimeoutException:
            print("Unstable connection detected. Wait for {} seconds. No data is pushed on IoT core from {} to {}.".format(DEFAULT_OPERATION_TIMEOUT_SEC, (datetime.datetime.now() - datetime.timedelta(seconds=DEFAULT_OPERATION_TIMEOUT_SEC)), datetime.datetime.now()))
        #print('Publish End')


    # Disconect operation for each devices
    def disconnect(self):
        self.myAWSIoTMQTTClient.disconnect()

def publish_data():
    for sensor in (soil_sensor_1, soil_sensor_2, soil_sensor_3, soil_sensor_4):
        sensor.publish()

# Main method with actual objects and method calling to publish the data in MQTT
# Again this is a minimal example that can be extended to incopporate more devices
# Also there can be different method calls as well based on the devices and their working.
if __name__ == '__main__':

    loopCount = 0
    scheduler = sched.scheduler(time.time, time.sleep)

    # SOil sensor device Objects
    soil_sensor_1 = AWS("SENS_01", "SENS_1.pem.crt", "SENS_1-private.pem.key")
    soil_sensor_2 = AWS("SENS_2", "SENS_2.pem.crt", "SENS_2-private.pem.key")
    soil_sensor_3 = AWS("SENS_3", "SENS_3.pem.crt", "SENS_3-private.pem.key")
    soil_sensor_4 = AWS("SENS_4", "SENS_3.pem.crt", "SENS_3-private.pem.key")

    now = time.time()

    while True:
        try :
            scheduler.enterabs(now+loopCount, 1, publish_data)
            loopCount += 2
            scheduler.run()
        except KeyboardInterrupt:
            break