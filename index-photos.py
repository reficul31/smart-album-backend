import boto3
import requests

from datetime import datetime

AWSAUTH = ('master', 'Columbia110x3$')
HEADERS = { "Content-Type": "application/json" }
CUSTOM_LABEL_FIELD_NAME = 'customlabels'
URL = "https://search-photos-ctm5peqt7woxp4qzhpvenm3p7y.us-east-1.es.amazonaws.com/photos-index/_doc"

def lambda_handler(event, context):
    print("Event: ", event)
    for record in event['Records']:
        photo = record['s3']['object']['key']
        bucket = record['s3']['bucket']['name']
        
        client = boto3.client('s3')
        response = client.head_object(Bucket=bucket, Key=photo)
        
        print("Head Object: {}".format(response["Metadata"]))
        labels, metadata = [], response['Metadata']
        if CUSTOM_LABEL_FIELD_NAME in metadata:
            print("Metadata: ", metadata)
            labels = [label.lower() for label in metadata[CUSTOM_LABEL_FIELD_NAME].split(",")]
        else:
            print("No custom labels for the image found")
        
        client = boto3.client('rekognition')
        response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MaxLabels=10)
        print("Rekognition Reponse: {}".format(response))
        labels = labels + [label['Name'].lower() for label in response['Labels']]
        
        createdTimestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        data = {'objectKey': photo, 'bucket': bucket, 'createdTimestamp': createdTimestamp, 'labels': labels}
        print("Data: {}".format(data))

        response = requests.post(URL, auth=AWSAUTH, json=data, headers=HEADERS)
        print("Response:", response)
