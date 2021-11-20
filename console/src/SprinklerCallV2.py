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


# READ FROM ENV
import os
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = os.path.abspath(os.getcwd())+'/.env'
load_dotenv(dotenv_path=env_path)
BUCKET_NAME=os.getenv("BUCKET_NAME")
INTERVAL_TIME=int(os.getenv("INTERVAL_TIME"))

EXP_MIN_MOISTER_VALUE=float(os.getenv("EXP_MIN_MOISTER_VALUE"))
EXP_MAX_MOISTER_VALUE=float(os.getenv("EXP_MAX_MOISTER_VALUE"))
MAINTAIN_MOISTER_VALUE=float(os.getenv("MAINTAIN_MOISTER_VALUE"))
EFF_ROOT_LEN=float(os.getenv("EFF_ROOT_LEN"))
LAND_SQM=float(os.getenv("LAND_SQM"))
PUMP_DIS_RATE_LTR_PER_SEC=float(os.getenv("PUMP_DIS_RATE_LTR_PER_SEC"))
OPEN_WEATHER_API_KEY=os.getenv("OPEN_WEATHER_API_KEY")

EXP_HUMID=float(os.getenv("EXP_HUMID"))

FC=float(os.getenv("FC"))
PWP=float(os.getenv("PWP"))

# Here we assign our aws clients/resources to use
iot_client = boto3.client('iot',region_name ='us-east-1')
s3 = boto3.resource(service_name = 's3')

farm_table_access = DataBase_Access_Model("farms")
device_table_access = DataBase_Access_Model("devices")
soil_table_access = DataBase_Access_Model("soildata")
sp_log_access = DataBase_Access_Model("sprinklerlogs")


farm_data={}

# OPEN WEATHER Initialization
owm = OWM(OPEN_WEATHER_API_KEY)
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
        s3.meta.client.upload_file(Filename = filename,Bucket=BUCKET_NAME,Key=key+filename)

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
        response = device_table_access.scan_table(Attr('farm_id').eq(farmdata['farm_id']) & Attr('type').eq('ss'))
        for device_data in response:
            if device_data['device_id'] not in farm_data[farmdata['farm_id']]['devices']:
                farm_data[farmdata['farm_id']]['devices'].append(device_data['device_id'])
        response = device_table_access.scan_table(Attr('farm_id').eq(farmdata['farm_id']) & Attr('type').eq('sp'))
        for sprinkler_data in response:
            if sprinkler_data['device_id'] not in farm_data[farmdata['farm_id']]['sprinkler']:
                farm_data[farmdata['farm_id']]['sprinkler'].append(sprinkler_data['device_id'])
    
def sprinkler_action():
    sp_id = threading.current_thread().name
    print("In sprinkler action, Device ID : "+sp_id)
    # FIND DATA FOR LAST X seconds - INTERVAL_TIME from .env 
    stop = (datetime.datetime.now())
    start = (stop - timedelta(seconds=INTERVAL_TIME))
    print("Data from :"+str(start))
    print("Data to :"+str(stop))
        
    device_table = DataBase_Access_Model("devices")
    soilss = device_table.get_by_condition('parent_id',sp_id)
    if(len(soilss)):
        for ss in soilss:
            # USE EXP_MAX_MOISTER_VALUE & EXP_MIN_MOISTER_VALUE value to eliminate bad data
            response = soil_table_access.scan_table(Attr('device_id').eq(ss['device_id']) & Attr('timestamp').between(str(start),str(stop)) & Attr('value').between(int(EXP_MIN_MOISTER_VALUE),int(EXP_MAX_MOISTER_VALUE)))
            data_point_count=0
            avg_soil = 0
            for soil_data in response:
                avg_soil += float(soil_data['value'])
                data_point_count+=1

        if data_point_count:
            avg_soil = avg_soil/data_point_count
            print("Total SS count : "+str(len(soilss)))
            print("Avg soil moister : "+str(avg_soil))
            if avg_soil<MAINTAIN_MOISTER_VALUE:

                # CHECK AWATHER IF ITS GOING TO RAIN - based on some percent of possibility
                should_irrigate = 1

                # CHECK FOR HUMIDITY 
                farm_table = DataBase_Access_Model("farms")
                farm = farm_table.get_by_condition('farm_id',ss['farm_id'])
                hum,temp = get_weather_data(float(farm[0]['lat']), float(farm[0]['long']))
                
                # Temp : cucumber plants is between 60-90 degrees Fahrenheit
                # keeping the humidity in the 60% range during the day and in the 80% range at night for cucumber
                # In our case EXP_HUMID = 70%

                if(hum > EXP_HUMID): 
                    should_irrigate = 0
                    print("Sprinkler:"+sp_id+" No action: Humidity is above expected range. Exp:"+str(EXP_HUMID)+" Location Humidity :"+str(hum))                    

                if(should_irrigate):
                    print("Required Sprinkler Action")
                    #AWC = FC - PWP - Goal is to maintain the FC point -- This is the moister % we'll get from device and then
                    moister_diff = MAINTAIN_MOISTER_VALUE-avg_soil
                    depth_of_irrigation = (moister_diff/100)*EFF_ROOT_LEN # cm of water should be applied once the moisture level goes below MAINTAIN_MOISTER_VALUE
                    water_to_be_applied = (depth_of_irrigation*LAND_SQM)/100 # IN Cu. m
                    required_ltr = water_to_be_applied*1000
                    required_time_in_sec=required_ltr/PUMP_DIS_RATE_LTR_PER_SEC # In Sec.

                    pump_start = (datetime.datetime.now())
                    pump_stop = (pump_start + timedelta(seconds=required_time_in_sec))
                    
                    # LOG THE DETTAILS 
                    print("Sprinkler:"+sp_id+" for "+str(required_time_in_sec)+' seconds')
                    print("Sprinkler:"+sp_id+" start at:"+str(pump_start))
                    print("Sprinkler:"+sp_id+" stop at:"+str(pump_stop))

                    #INSERT IN LOG TABLE
                    log_data={}
                    log_data['device_id']=sp_id
                    log_data['timestamp']= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_data['farm_id']= ss['farm_id']
                    log_data['water_duration']= str(required_time_in_sec)
                    log_data['water_ltr']= str(required_ltr)
                    log_data['start_time']= str(pump_start)
                    log_data['stop_time']= str(pump_stop)
                    log_data['action_taken']= str(1) # Means we have decided to irrigate 
                    log_data['note']= str(hum)
                    log_data['device_state']= "On"

                    
                    sprinklerlogs_table = DataBase_Access_Model("sprinklerlogs")
                    sprinklerlogs_table.insert_data(log_data)

                    # SEND SMS OR SOME NOTIFICATION OR TRIGGER TO Actually ON pump or sprinkler NOW
            else:
                print("MAINTAIN_MOISTER_VALUE : "+str(MAINTAIN_MOISTER_VALUE)+" Current Value :"+str(avg_soil)+", No Action Required "+sp_id)
        else:
            print("No Data point available for this device")

    else:
        print("No SS attached to this SP")

    #time.sleep(INTERVAL_TIME)
    print("Excution Finished for "+threading.current_thread().name);

    # avg_soil = 0
    # stop = (datetime.datetime.now())
    # start = (stop - timedelta(seconds=15))
    # for farm_id, data in farm_data.items():
    #     try:
    #         if farm_id == f_id:
    #             print("Found farm")
    #             for device in data['devices']:
    #                 response = soil_table_access.scan_table(Attr('deviceid').eq(device) & Attr('timestamp').between(str(start),str(stop)))
    #                 for soil_data in response:
    #                     avg_soil += float(soil_data['value'])
    #             avg_soil = avg_soil/len(data['devices'])
    #             print(avg_soil)
    #             if avg_soil < 30:
    #                 message={}
    #                 message['Farm_ID'] = farm_id
    #                 for sprinkler in data['sprinkler']:
    #                     device_table_access.update_value(sprinkler, farm_id, 'on')
    #                     message['Sprinkler_ID'] = sprinkler
    #                     message['Timestamp'] = str(datetime.datetime.now())
    #                     message['Status']='ON'
    #                     write_agri_data_tos3(message)
    #                     time.sleep(tmr_val)
    #                     device_table_access.update_value(sprinkler, farm_id, 'off')
    #                     message['Timestamp'] = str(datetime.datetime.now())
    #                     message['Status']='OFF'
    #                     write_agri_data_tos3(message)
    #     except KeyboardInterrupt:
    #         break;
        
        
    
# def loop_func():
#     timer_val = 0
#     for i in range(len(lat)):
#         temp, hum = get_weather_data(float(lat[i]), float(long[i]))
#         avg_temp[i] += temp
#         avg_hum[i] += hum

#     if loopCount % 15 == 0:
#         for i in range(len(avg_temp)):
#             avgt = avg_temp[i]/5.0
#             avgh = avg_hum[i]/5.0
#             temp_diff = abs(ideal_temp - avgt)
#             hum_diff = abs(ideal_hum - avgh)
#             timer_val = int((temp_diff + hum_diff)/2)
#             print(timer_val)
#             avg_temp[i] = 0
#             avg_hum[i] = 0 
        
#         print("Starting threads")
#         t1 = threading.Thread(target=sprinkler_action, name='farm_1', args=('F001', timer_array[timer_val]))
#         #t2 = threading.Thread(target=sprinkler_action, name='farm_2', args=('farm_02', timer_array[timer_val]))
#         #t3 = threading.Thread(target=sprinkler_action, name='farm_3', args=('farm_03', timer_array[timer_val]))
#         #t4 = threading.Thread(target=sprinkler_action, name='farm_4', args=('farm_04', timer_array[timer_val]))
#         #t5 = threading.Thread(target=sprinkler_action, name='farm_5', args=('farm_05', timer_array[timer_val]))
#         t1.start()
#         #t2.start()
#         #t3.start()
#         #t4.start()
#         #t5.start()
#         t1.join()
#         #t2.join()
#         #t3.join()
#         #t4.join()
#         #t5.join()
#=============================
# def loop_func():
#     timer_val = 0
#     for i in range(len(lat)):
#         temp, hum = get_weather_data(float(lat[i]), float(long[i]))
#         avg_temp[i] += temp
#         avg_hum[i] += hum

#     if loopCount % 15 == 0:
#         for i in range(len(avg_temp)):
#             avgt = avg_temp[i]/5.0
#             avgh = avg_hum[i]/5.0
#             temp_diff = abs(ideal_temp - avgt)
#             hum_diff = abs(ideal_hum - avgh)
#             timer_val = int((temp_diff + hum_diff)/2)
#             if timer_val > 9:
#                 timer_val = 9
#             print(timer_val)
#             avg_temp[i] = 0
#             avg_hum[i] = 0 
        
#         print("Starting threads")
#         t1 = threading.Thread(target=sprinkler_action, name='farm_1', args=('F001', timer_array[timer_val]))
#         #t2 = threading.Thread(target=sprinkler_action, name='farm_2', args=('farm_02', timer_array[timer_val]))
#         #t3 = threading.Thread(target=sprinkler_action, name='farm_3', args=('farm_03', timer_array[timer_val]))
#         #t4 = threading.Thread(target=sprinkler_action, name='farm_4', args=('farm_04', timer_array[timer_val]))
#         #t5 = threading.Thread(target=sprinkler_action, name='farm_5', args=('farm_05', timer_array[timer_val]))
#         t1.start()
#         #t2.start()
#         #t3.start()
#         #t4.start()
#         #t5.start()
#         t1.join()
#         #t2.join()
#         #t3.join()
#         #t4.join()
#         #t5.join()
    
    
if __name__ == '__main__':
    #  GET sprinkler device 
    device_table = DataBase_Access_Model("devices")
    sprinklers = device_table.get_by_condition('device_type','sp')
    thrds = {}
    for sp in sprinklers:
        print("Preparing Data for: "+sp['device_id'])
        thrds[sp['device_id']] = threading.Thread(target=sprinkler_action,name=sp['device_id'])
        #ss_sensors[ss['device_id']] = AWS(ss['device_id'], ss['device_id']+"_cert.pem", ss['device_id']+"_private.key") 
    
    for th in thrds:
        print("Starting thread .. "+th)
        thrds[th].start();

    for th in thrds:
        thrds[th].join();
        print("Closing thread .. "+th)

    print("Closing sprinkler actions")
