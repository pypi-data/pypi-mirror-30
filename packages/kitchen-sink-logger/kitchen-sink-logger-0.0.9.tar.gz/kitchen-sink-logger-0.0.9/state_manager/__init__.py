import boto3
import json
from botocore.exceptions import ClientError
from backpack import Backpack

class StateManager(object):
    def __init__(self, **kwargs):
        table_name = kwargs.pop('TableName', 'BackpackState')
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(table_name)
    
    def upsert(self, backpack, **kwargs):
        state_id = kwargs.get('StateId', backpack.id)
        response = self.table.put_item(
            Item={
                'state_id': state_id,
                'perm_items': backpack.perm_items,
                'metrics': backpack.metrics,
                'timers': backpack.timers
            }
        )
        
    def get(self, state_id):
        try:
            response = self.table.get_item(
                Key={
                    'state_id': state_id
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            b = Backpack().from_json(json.dumps(response['Item']))
            return b