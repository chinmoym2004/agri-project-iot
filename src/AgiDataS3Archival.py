import csv
import boto3
import datetime
from datetime import datetime
import os.path

# Here we assign our aws clients/resources to use
iot_client = boto3.client('iot',region_name ='us-east-1')
s3 = boto3.resource(service_name = 's3')

# Write Data to s3 here. Call this method and pass a dictionary
def write_agri_data_tos3(data):
    if len(data.keys()) != 0:
        Farm = data['Farm_ID']
        timestamp = data['Timestamp']
        date_time_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
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
        

test_data = {"Farm_ID":"farm_2", "Timestamp":"2021-10-30 17:15:27", "Sprinkler_ID":"SPR_02", "Status": "ON"}
write_agri_data_tos3(test_data)