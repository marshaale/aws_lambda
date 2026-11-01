import json
import boto3

ec2_client = boto3.client("ec2")
config_client = boto3.client("config")


def lambda_handler(event, context):
    invoking_event = json.loads(event["invokingEvent"])

    configuration_item = invoking_event.get("configurationItem", {})

    resource_type = configuration_item.get("resourceType")
    resource_id = configuration_item.get("resourceId")
    configuration_item_status = configuration_item.get("configurationItemStatus")

    if resource_type != "AWS::EC2::Instance":
        return

    if configuration_item_status in ["ResourceDeleted", "ResourceDeletedNotRecorded"]:
        return

    compliance_status = "NON_COMPLIANT"
    annotation = "EC2 detailed monitoring is disabled."

    try:
        response = ec2_client.describe_instances(
            InstanceIds=[resource_id]
        )

        instances = [
            instance
            for reservation in response["Reservations"]
            for instance in reservation["Instances"]
        ]

        if not instances:
            return
        
        instance = instances[0]
        if instance["Monitoring"]["State"] == "enabled":
            compliance_status = "COMPLIANT"
            annotation = "EC2 detailed monitoring is enabled."

    except Exception as error:
        print(f"Error checking instance {resource_id}: {error}")

    evaluation = {
        "ComplianceResourceType": resource_type,
        "ComplianceResourceId": resource_id,
        "ComplianceType": compliance_status,
        "Annotation": annotation[:256],
        'OrderingTimestamp': invoking_event['notificationCreationTime']

    }

    config_client.put_evaluations(
        Evaluations=[evaluation],
        ResultToken=event["resultToken"]
    )

    print("Evaluation:", evaluation)

    return evaluation
