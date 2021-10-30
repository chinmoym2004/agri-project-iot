#Import Boto3 for accessing AWS features
import boto3
import time
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

class Database:
    # Get the dynamoDB service resource
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.client = boto3.client('dynamodb')

    # This method is used to create DynamoDB table
    def create_table(self, tablename, key_schema, attribute_definitions, provisioned_throughput):
        table = self.dynamodb.create_table(
            TableName = tablename,
            KeySchema = key_schema,
            AttributeDefinitions = attribute_definitions,
            ProvisionedThroughput = provisioned_throughput
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=tablename)
        return ("Table item count =" + str(table.item_count))

    # This method inserts a single document
    def put_item(self, tablename, item):
        table = self.dynamodb.Table(tablename)
        table.put_item(
            Item = item
        )

    # This method finds a single item using the information provided in the key
    def get_item(self, tablename, key):
        table = self.dynamodb.Table(tablename)
        response = table.get_item(
            Key = key
        )
        item = response['Item']
        return item

    # This methods updates an item using the information provided in the key
    def update_item(self, tablename, key, updateExpression, expressionAttrVal):
        table = self.dynamodb.Table(tablename)
        table.update_item(
            Key = key,
            UpdateExpression = updateExpression,
            ExpressionAttributeValues = expressionAttrVal
        )

    # This method deletes an item from the table
    def delete_item(self, tablename, key):
        table = self.dynamodb.Table(tablename)
        table.delete_item(
            Key = key
        )

    # This method queries the table using the key information
    def query_items(self, tablename, key):
        table = self.dynamodb.Table(tablename)
        response = table.query(
            KeyConditionExpression = key
        )
        items = response['Items']
        return items

    # This method is used to scan the table using the filterexpression
    def scan_table(self, tablename, filterexpression):
        table = self.dynamodb.Table(tablename)
        response = table.scan(
            FilterExpression = filterexpression
        )
        items = response['Items']
        return items

    # This method is used to write items in a batch
    def batch_writer(self, tablename, batchdata):
        table = self.dynamodb.Table(tablename)
        with table.batch_writer() as batch:
            for data in batchdata:
                batch.put_item(
                    Item = data
                )

    # This method is used tto delete the entire table
    def delete_table(self, tablename):
        table = self.dynamodb.Table(tablename)
        table.delete()
    
    def resource_check(self, tablename):
        tables = self.client.list_tables()['TableNames']
        if tablename in tables:
            return True
        else:
            return False

_aws_dynamodb = Database()       
class DataBase_Access_Model():
    def __init__(self, tablename):
        self._tablename = tablename

    # This method is used to pass parameters in the required format for the creation of dynamodb table
    def createtable(self, primary_key, partition_key, pri_attr, part_attr, throughput):
        keyscheme = [{'AttributeName': primary_key,
                      'KeyType': 'HASH'},
                     {'AttributeName': partition_key,
                      'KeyType': 'RANGE'}]
        attributedef = [{'AttributeName': primary_key,
                         'AttributeType': pri_attr},
                        {'AttributeName': partition_key,
                         'AttributeType': part_attr}]
        throughput = {'ReadCapacityUnits': throughput,
                      'WriteCapacityUnits': throughput}
        result = _aws_dynamodb.create_table(self._tablename, keyscheme, attributedef, throughput)
        return result

    def scantable_between_attribute(self, key, parameter1, parameter2):
        response = _aws_dynamodb.scan_table(self._tablename, Attr(key).between(parameter1, parameter2))
        return response

    # This method inserts a single aggregate data to the dynamodb table
    def insert_data(self, data):
        _aws_dynamodb.put_item(self._tablename, data)

    # This method inserts batched data into dynamodb table
    def insert_data_batch(self, batch_data):
        batchdataitems = []
        for data in batch_data:
            batchdataitems.append(data)
        _aws_dynamodb.batch_writer(self._tablename, batchdataitems)

    # This method is used to delete the table
    def delete_table_and_data(self):
        result = _aws_dynamodb.delete_table(self._tablename)
        return result
        
    def resource_in_use_check(self):
        if _aws_dynamodb.resource_check(self._tablename):
            return True
        return False
        
        
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