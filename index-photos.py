import boto3
import requests

from datetime import datetime

AWSAUTH = ('', '')
HEADERS = { "Content-Type": "application/json" }
CUSTOM_LABEL_FIELD_NAME = 'x-amz-meta-customLabels'

URL = ""

def lambda_handler(event, context):
    print("Event: ", event)
    for record in event['Records']:
        photo = record['s3']['object']['key']
        bucket = record['s3']['bucket']['name']
        
        client = boto3.client('s3')
        response = client.head_object(Bucket=bucket, Key=photo)
        labels, metadata = [], response['Metadata']
        if CUSTOM_LABEL_FIELD_NAME in metadata:
            print("Metadata: ", metadata)
            labels.append(metadata[CUSTOM_LABEL_FIELD_NAME])
        else:
            print("No custom labels for the image found")
        
        client = boto3.client('rekognition')
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MaxLabels=10)
        labels = labels + [label['Name'] for label in response['Labels']]
        
        createdTimestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        data = {'objectKey': photo, 'bucket': bucket, 'createdTimestamp': createdTimestamp, 'labels': labels}
        print("Data: {}".format(data))

        response = requests.post(URL, auth=AWSAUTH, json=data, header=HEADERS)
