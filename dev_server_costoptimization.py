import json
import boto3

def lambda_handler(event, context):
    print("event:", event)
    region = event.get('region', 'us-east-1')
    action = event.get('action', 'start')
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances(
        Filters=[{
            'Name': 'tag:Environment',
            'Values': ['development']
        }]
    )
    instances_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instances_ids.append(instance_id)
            print(f"Found EC2 instance: {instance_id}")

    if not instances_ids:
        print(f"action: {action} was not processed due to lack of instances")
        return
     
    if action == 'start':
        ec2.start_instances(InstanceIds=instances_ids)
        print("Starting instance...")
    elif action == 'stop':
        ec2.stop_instances(InstanceIds=instances_ids)
        print("Stopping instance...")
    else:
        print(f"Unknown action: {action}")
        return

    return {
        'statusCode': 200,
        'body': json.dumps(f'{action} instance request processed')
    }
