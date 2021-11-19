from database import DataBase_Access_Model
import datetime
from datetime import timedelta

if __name__ == '__main__':
    #  GET sprinkler device where the time has crossed current time
    sprinklerlogs_table = DataBase_Access_Model("sprinklerlogs")
    now_time = datetime.datetime.now()
    sprinklers = sprinklerlogs_table.scan_table(Attr('stop_time').lt(str(now_time)))
    for sp in sprinklers:
        sprinklerlogs_table.update_sprinkler_status_value(sp['device_id'],sp['timestamp'],'OFF')
        print(sp['device_id']+" is OFF now");