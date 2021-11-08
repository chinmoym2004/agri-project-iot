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
        print(key,updateExpression,expressionAttrVal)
        table = self.dynamodb.Table(tablename)
        response = table.update_item(
            Key = key,
            UpdateExpression = updateExpression,
            ExpressionAttributeValues = expressionAttrVal,
            ReturnValues="UPDATED_NEW"
        )
        print(response)
        return response

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
        
    def scan_entire_table(self, tablename):
        table = self.dynamodb.Table(tablename)
        response = table.scan()
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

    def get_by_condition_expression(self, tablename,field,data):
        table = self.dynamodb.Table(tablename)
        response = table.scan(
            FilterExpression= Attr(field).eq(data)
        )
        items = response['Items']
        return items

dynamo = Database()

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
        result = dynamo.create_table(self._tablename, keyscheme, attributedef, throughput)
        return result
        
    def query_table(self, key):
        return dynamo.query_items(self._tablename, Key('farm_id').eq(key))

    def scan_table(self, filter_experssion):
        response = dynamo.scan_table(self._tablename, filter_experssion)
        return response
    
    def update_value(self, part_key, sort_key, expressionAttrVal):
        return dynamo.update_item(self._tablename,{'device_id': part_key, 'farm_id': sort_key},'set device_state = :r',{':r':expressionAttrVal,})
    
    def scan_all_items(self):
        return dynamo.scan_entire_table(self._tablename)

    # This method inserts a single aggregate data to the dynamodb table
    def insert_data(self, data):
        dynamo.put_item(self._tablename, data)

    # This method inserts batched data into dynamodb table
    def insert_data_batch(self, batch_data):
        batchdataitems = []
        for data in batch_data:
            batchdataitems.append(data)
        dynamo.batch_writer(self._tablename, batchdataitems)
        
    def get_data(self,sort_key, part_key):
        return(dynamo.get_item(self._tablename,{'device_id':sort_key,'farm_id':part_key}))

    def get_by_condition(self,field,data):
        return (dynamo.get_by_condition_expression(self._tablename,field,data));

    def get_data_by_type(self,data):
        return(dynamo.query_items(self._tablename,data))

    # This method is used to delete the table
    def delete_table_and_data(self):
        result = dynamo.delete_table(self._tablename)
        return result
        
    def resource_in_use_check(self):
        if dynamo.resource_check(self._tablename):
            return True
        return False