################################################### Connecting to AWS
import boto3

import json
################################################### Create random name for things
import random
import string
import os

################################################### Parameters for Thing
thingArn = ''
thingId = ''
#thingName = 'SS1'
defaultPolicyName = 'AgriCore-policy' # Should Exist in account https://console.aws.amazon.com/iot/home?region=us-east-1#/policyhub
PATH_TO_CERT = os.path.dirname(os.path.abspath(__file__))+'/../config/'
###################################################

def createThing(thingName):

	global thingClient

	thingResponse = thingClient.create_thing(
	  thingName = thingName
	)

	data = json.loads(json.dumps(thingResponse, sort_keys=False, indent=4))

	#print(data);

	for element in data: 
	  if element == 'thingArn':
	      thingArn = data['thingArn']
	  elif element == 'thingId':
	      thingId = data['thingId']

	createCertificate(thingName)



def createCertificate(thingName):
	global thingClient
	certResponse = thingClient.create_keys_and_certificate(
			setAsActive = True
	)
	data = json.loads(json.dumps(certResponse, sort_keys=False, indent=4))
	for element in data: 
			if element == 'certificateArn':
					certificateArn = data['certificateArn']
			elif element == 'keyPair':
					PublicKey = data['keyPair']['PublicKey']
					PrivateKey = data['keyPair']['PrivateKey']
			elif element == 'certificatePem':
					certificatePem = data['certificatePem']
			elif element == 'certificateId':
					certificateId = data['certificateId']
							
	with open(PATH_TO_CERT+thingName+'_public.key', 'w') as outfile:
			outfile.write(PublicKey)
	with open(PATH_TO_CERT+thingName+'_private.key', 'w') as outfile:
			outfile.write(PrivateKey)
	with open(PATH_TO_CERT+thingName+'_cert.pem', 'w') as outfile:
			outfile.write(certificatePem)

	response = thingClient.attach_policy(
			policyName = defaultPolicyName,
			target = certificateArn
	)
	response = thingClient.attach_thing_principal(
			thingName = thingName,
			principal = certificateArn
	)

thingClient = boto3.client('iot')
#createThing()