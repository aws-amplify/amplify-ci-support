import boto3
import cfnresponse
import sys
import traceback

def handle_delete(df, event):
    arn = event['PhysicalResourceId']
    df.delete_project(
        arn = arn
    )
    return arn

def handle_update(df, event):
    arn = event['PhysicalResourceId']
    df.update_project(
        arn = arn,
        name = event['ResourceProperties']['ProjectName']
    )
    return arn

def handle_create(df, event):
    resp = df.create_project(
        name = event['ResourceProperties']['ProjectName']
    )
    return resp['project']['arn']

def get_top_device_pool(df, df_project_arn):
    try:
        resp = df.list_device_pools(
            arn=df_project_arn,
            type='CURATED'
        )
        pools = resp['devicePools']
        for pool in pools:
            if pool['name'] == 'Top Devices':
                return pool['arn']
    except:
        print("Unable to get device pools: ", sys.exc_info()[0])
    return None
    
def handler(event, context):
    df = boto3.client('devicefarm', region_name='us-west-2')
    project_arn = None
    try:
        if event['RequestType'] == 'Delete':
            project_arn = handle_delete(df, event)
        
        if event['RequestType'] == 'Update':
            project_arn = handle_update(df, event)
        
        if event['RequestType'] == 'Create':
            project_arn = handle_create(df, event)
        
        device_pool_arn = get_top_device_pool(df, project_arn)
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Arn' : project_arn, 'DevicePoolArn': device_pool_arn}, project_arn)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        traceback.print_exc()
        cfnresponse.send(event, context, cfnresponse.FAILED, None, None)