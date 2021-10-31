import os

PATH_TO_CERT = os.path.dirname(os.path.abspath(__file__))+'/console/config'
caPath = PATH_TO_CERT + "/" + 'AmazonRootCA1.pem'
certPath = PATH_TO_CERT + "/" + 'SENS_2.pem.crt'
keyPath = PATH_TO_CERT + "/" + 'SENS_2-private.pem.key'

topic = "iot/agritech"

awshost = os.getenv("ENDPOINT")
awsport = 8883
clientId = 'agritech_1'
thingName = 'debug_1'