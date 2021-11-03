from database import DataBase_Access_Model
        
if __name__ == '__main__':
    farm_table = DataBase_Access_Model("Farm")
    if farm_table.resource_in_use_check():
        farm_table.delete_table_and_data()
        time.sleep(2)
    farm_table.createtable("farm_id", "name", "S", "S", 5)
    device_table = DataBase_Access_Model("Device")
    if device_table.resource_in_use_check():
        device_table.delete_table_and_data()
        time.sleep(2)
    device_table.createtable("device_id", "farm_id", "S", "S", 5)