from database import DataBase_Access_Model
import datetime,time
import createThings

farms = [
    {
        'farm_id' : 'F001',
        'label' : 'Fresh to Home',
        'long':'78.3407965',
        'lat': '17.4628965',
        'location':'Chennai',
        'crop_type':'Cucumber',
        'root_depth':'24', #inches
        'land_area':'10000', # sq. m
        'mad':'50', # 50%
        'soil_type':'silt',
        'min_moister_leve':'24', # 24%
        'max_moister_leve':'32' # 32%

    },
    {
        'farm_id': 'F002',
        'label' : 'Green land',
        'long':'80.138236',
        'lat':'12.9298971',
        'location':'Chennai',
        'crop_type':'Cucumber',
        'root_depth':'24', #inches
        'land_area':'10000', # sq. m
        'mad':'50', # 50%
        'soil_type':'silt',
        'min_moister_leve':'24', # 24%
        'max_moister_leve':'32' # 32%
    },
    {
        'farm_id': 'F003',
        'label' : 'Tomato Land',
        'long':'87.5679722',
        'lat': '22.7224444',
        'location':'Chennai',
        'crop_type':'Cucumber',
        'root_depth':'24', #inches
        'land_area':'10000', # sq. m
        'mad':'50', # 50%
        'soil_type':'silt',
        'min_moister_leve':'24', # 24%
        'max_moister_leve':'32' # 32%
    },
    {
        'farm_id': 'F004',
        'label' : 'Dragon Land',
        'long':'77.9467335',
        'lat': '10.2087529',
        'location':'Chennai',
        'crop_type':'Cucumber',
        'root_depth':'24', #inches
        'land_area':'10000', # sq. m
        'mad':'50', # 50%
        'soil_type':'silt',
        'min_moister_leve':'24', # 24%
        'max_moister_leve':'32' # 32%
    }
]

devices = [
    # Farm 1 - F001
    {
        'device_id':'SS001',
        'label':'Soil Sensor 1',
        'device_type':'ss',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F001',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS002',
        'device_type':'ss',
        'label':'Soil Sensor 2',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F001',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS003',
        'device_type':'ss',
        'label':'Soil Sensor 3',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F001',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS004',
        'device_type':'ss',
        'label':'Soil Sensor 4',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F001',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SP001',
        'device_type':'sp',
        'label':'Sprinkler 1',
        'device_status':1,
        'farm_id':'F001',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    # Farm 2 - F002
    {
        'device_id':'SS005',
        'device_type':'ss',
        'label':'Soil Sensor 5',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F002',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS006',
        'device_type':'ss',
        'label':'Soil Sensor 6',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F002',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS007',
        'device_type':'ss',
        'label':'Soil Sensor 7',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F002',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS008',
        'device_type':'ss',
        'label':'Soil Sensor 8',
        'parent_id':'SP001',
        'device_status':1,
        'farm_id':'F002',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SP002',
        'device_type':'sp',
        'label':'Sprinkler 2',
        'device_status':1,
        'farm_id':'F003',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    # Farm 3 - F003
    {
        'device_id':'SS009',
        'device_type':'ss',
        'parent_id':'SP003',
        'label':'Soil Sensor 9',
        'device_status':1,
        'farm_id':'F003',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS0010',
        'device_type':'ss',
        'parent_id':'SP003',
        'label':'Soil Sensor 10',
        'device_status':1,
        'farm_id':'F003',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS0011',
        'device_type':'ss',
        'parent_id':'SP003',
        'label':'Soil Sensor 11',
        'device_status':1,
        'farm_id':'F003',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS0012',
        'device_type':'ss',
        'parent_id':'SP003',
        'label':'Soil Sensor 12',
        'device_status':1,
        'farm_id':'F003',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SP003',
        'device_type':'sp',
        'device_status':1,
        'label':'Sprinkler 3',
        'farm_id':'F003',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    # Farm 4 - F004
    {
        'device_id':'SS0013',
        'device_type':'ss',
        'parent_id':'SP004',
        'label':'Soil Sensor 13',
        'device_status':1,
        'farm_id':'F004',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS0014',
        'device_type':'ss',
        'parent_id':'SP004',
        'label':'Soil Sensor 14',
        'device_status':1,
        'farm_id':'F004',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS0015',
        'device_type':'ss',
        'parent_id':'SP004',
        'label':'Soil Sensor 15',
        'device_status':1,
        'farm_id':'F004',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SS0016',
        'device_type':'ss',
        'parent_id':'SP004',
        'label':'Soil Sensor 16',
        'device_status':1,
        'farm_id':'F004',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'device_id':'SP004',
        'device_type':'sp',
        'label':'Sprinkler 4',
        'device_status':1,
        'farm_id':'F004',
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
]
        
if __name__ == '__main__':
    #Create the Farms 

    farm_table = DataBase_Access_Model("farms")
    if farm_table.resource_in_use_check():
        farm_table.delete_table_and_data()
    time.sleep(2)
    farm_table.createtable("farm_id", "label", "S", "S", 5)
        
    # Create the Devices

    device_table = DataBase_Access_Model("devices")
    if device_table.resource_in_use_check():
        device_table.delete_table_and_data()
    time.sleep(2)
    device_table.createtable("device_id", "farm_id", "S", "S", 5)


    # Create Soil Record Table 
    soil_table = DataBase_Access_Model("soildata")
    if soil_table.resource_in_use_check():
        soil_table.delete_table_and_data()
    time.sleep(2)
    soil_table.createtable("device_id", "timestamp", "S", "S", 5)
    


    # Insert Farm Data
    for farm in farms:
        #print(farm)
        farm_table.insert_data(farm)

    # Insert Device Data
    for device in devices:
        #print(device)
        device_table.insert_data(device)
        # create the Thing 
        createThings.createThing(device['device_id'])