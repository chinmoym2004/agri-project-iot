from pyowm import OWM
import json
from database import DataBase_Access_Model
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
import random
import datetime
import sched
import time
import csv
import os.path
import boto3
import threading
from datetime import timedelta 

# Here we assign our aws clients/resources to use
iot_client = boto3.client('iot',region_name ='us-east-1')
s3 = boto3.resource(service_name = 's3')

farm_table_access = DataBase_Access_Model("Farm")
device_table_access = DataBase_Access_Model("Device")
soil_table_access = DataBase_Access_Model("soil_sensor_data")

farm_data={}

owm = OWM('dc57f8d11379c7f3e5a213d7c1c19712')
mgr = owm.weather_manager()

lat = []
long = []
avg_temp = []
avg_hum = []

timer_array = [5,10,15,20,25,30,35,40,45,50]
ideal_temp = 35
ideal_hum = 20

def write_agri_data_tos3(data):
    if len(data.keys()) != 0:
        Farm = data['Farm_ID']
        timestamp = data['Timestamp']
        date_time_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        month = date_time_obj.month
        year = date_time_obj.year
        day = date_time_obj.day
        key = "AgriTechS3Logs/"+ Farm + "/" + str(year) + "/" + str(month) + "/"
        filename = Farm + "-" + str(year) + "-" + str(month) + "-" + str(day) + ".csv"
        file_exists = os.path.isfile(filename)
        with open(filename,'a') as f:
            fieldnames = ['Farm_ID','Timestamp','Sprinkler_ID','Status']
            dict_writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                dict_writer.writeheader()
            dict_writer.writerow({'Farm_ID': data['Farm_ID'],'Timestamp': data['Timestamp'],'Sprinkler_ID': data['Sprinkler_ID'],'Status': data['Status']})
        s3.meta.client.upload_file(Filename = filename,Bucket="kbgl-agridata",Key=key+filename)

def get_weather_data(user_lat, user_lon):
    one_call = mgr.one_call(lat=user_lat, lon=user_lon)
    current_data = (one_call.current.__dict__)
    return (current_data["humidity"],(current_data["temp"]["temp"] - 273.15))

def get_farm_parameters():    
    response = farm_table_access.scan_all_items()
    for farmdata in response:
        if farmdata['farm_id'] not in farm_data:
            farm_data[farmdata['farm_id']] = {}
        farm_data[farmdata['farm_id']]['lat'] = farmdata['lat']
        farm_data[farmdata['farm_id']]['long'] = farmdata['long']
        farm_data[farmdata['farm_id']]['devices'] = []
        farm_data[farmdata['farm_id']]['sprinkler'] = []
        response = device_table_access.scan_table(Attr('farm_id').eq(farmdata['farm_id']) & Attr('type').eq('soil_sensor'))
        for device_data in response:
            if device_data['device_id'] not in farm_data[farmdata['farm_id']]['devices']:
                farm_data[farmdata['farm_id']]['devices'].append(device_data['device_id'])
        response = device_table_access.scan_table(Attr('farm_id').eq(farmdata['farm_id']) & Attr('type').eq('sprinkler'))
        for sprinkler_data in response:
            if sprinkler_data['device_id'] not in farm_data[farmdata['farm_id']]['sprinkler']:
                farm_data[farmdata['farm_id']]['sprinkler'].append(sprinkler_data['device_id'])
    
def sprinkler_action(f_id, tmr_val):
    avg_soil = 0
    stop = (datetime.datetime.now())
    start = (stop - timedelta(seconds=15))
    for farm_id, data in farm_data.items():
        try:
            if farm_id == f_id:
                print("Found farm")
                for device in data['devices']:
                    response = soil_table_access.scan_table(Attr('deviceid').eq(device) & Attr('timestamp').between(str(start),str(stop)))
                    for soil_data in response:
                        avg_soil += float(soil_data['value'])
                avg_soil = avg_soil/len(data['devices'])
                print(avg_soil)
                if avg_soil < 30:
                    message={}
                    message['Farm_ID'] = farm_id
                    for sprinkler in data['sprinkler']:
                        device_table_access.update_value(sprinkler, farm_id, 'on')
                        message['Sprinkler_ID'] = sprinkler
                        message['Timestamp'] = str(datetime.datetime.now())
                        message['Status']='ON'
                        write_agri_data_tos3(message)
                        time.sleep(tmr_val)
                        device_table_access.update_value(sprinkler, farm_id, 'off')
                        message['Timestamp'] = str(datetime.datetime.now())
                        message['Status']='OFF'
                        write_agri_data_tos3(message)
        except KeyboardInterrupt:
            break;
        
        
    
def loop_func():
    timer_val = 0
    for i in range(len(lat)):
        temp, hum = get_weather_data(float(lat[i]), float(long[i]))
        avg_temp[i] += temp
        avg_hum[i] += hum

    if loopCount % 15 == 0:
        for i in range(len(avg_temp)):
            avgt = avg_temp[i]/5.0
            avgh = avg_hum[i]/5.0
            temp_diff = abs(ideal_temp - avgt)
            hum_diff = abs(ideal_hum - avgh)
            timer_val = int((temp_diff + hum_diff)/2)
            print(timer_val)
            avg_temp[i] = 0
            avg_hum[i] = 0 
        
        print("Starting threads")
        t1 = threading.Thread(target=sprinkler_action, name='farm_1', args=('farm_01', timer_array[timer_val]))
        #t2 = threading.Thread(target=sprinkler_action, name='farm_2', args=('farm_02', timer_array[timer_val]))
        #t3 = threading.Thread(target=sprinkler_action, name='farm_3', args=('farm_03', timer_array[timer_val]))
        #t4 = threading.Thread(target=sprinkler_action, name='farm_4', args=('farm_04', timer_array[timer_val]))
        #t5 = threading.Thread(target=sprinkler_action, name='farm_5', args=('farm_05', timer_array[timer_val]))
        t1.start()
        #t2.start()
        #t3.start()
        #t4.start()
        #t5.start()
        t1.join()
        #t2.join()
        #t3.join()
        #t4.join()
        #t5.join()
    
    
if __name__ == '__main__':
    loopCount = 0
    get_farm_parameters()
    for farmid, data in farm_data.items():
        lat.append(data['lat'])
        long.append(data['long'])
        avg_temp.append(0)
        avg_hum.append(0)
        
    scheduler = sched.scheduler(time.time, time.sleep)
    now = time.time()
    
    while True:
        try :
            scheduler.enterabs(now+loopCount, 1, loop_func)
            loopCount += 3
            scheduler.run()
        except KeyboardInterrupt:
            break
