import boto3
import random
import string
import requests

AWSAUTH = ('master', 'Columbia110x3$')
HEADERS = { "Content-Type": "application/json" }
SLOT_KEY_1 = 'Keyword1'
SLOT_KEY_2 = 'Keyword2'
OPEN_SERVICE_URL = 'https://search-photos-ctm5peqt7woxp4qzhpvenm3p7y.us-east-1.es.amazonaws.com/photos-index/_search?q=labels:{}'
S3_URL = "https://{}.s3.amazonaws.com/{}"

def send_response(photos):
    return {'results': [{
        'url': S3_URL.format(photo['bucket'], photo['objectKey']),
        'labels': photo['labels']
    } for photo in photos]}

def lambda_handler(event, context):
    print("Event: {}".format(event))
    
    if 'q' not in event:
        return {
            'code': 400,
            'message': "Query parameter not specified in the request"
        }
    
    userSearchQuery = event['q']
    print("Received user search query: {}".format(userSearchQuery))
    client = boto3.client("lexv2-runtime")
    response = client.recognize_text(
        botId='OIZMTO0GTX',
        botAliasId='QPY5ZFCKA9',
        localeId='en_US',
        sessionId=''.join(random.choices(string.ascii_lowercase, k=5)),
        text=userSearchQuery
    )
    
    interpretations = response.get('interpretations', None)
    if interpretations is None:
        print("Interpretations don't have any slots: {}".format(interpretations))
        return None
    
    print("Interpretations: {}".format(interpretations))
    slots = interpretations[0]['intent']['slots']
    
    queries = []
    print("Slots: {}".format(slots))
    if SLOT_KEY_1 in slots and slots[SLOT_KEY_1] is not None:
        queries.append(slots[SLOT_KEY_1]['value']['originalValue'])
    
    if SLOT_KEY_2 in slots and slots[SLOT_KEY_2] is not None:
        queries.append(slots[SLOT_KEY_2]['value']['originalValue'])
    
    if len(queries) == 0:
        print("No queries found.")
        return None
    
    queries = list(set(queries))
    print("Queries: {}".format(queries))
    
    for q in queries:
        if q.endswith("s"):
            queries.append(q[:len(q)-1])
    
    photos = []
    for q in queries:
        response = requests.get(OPEN_SERVICE_URL.format(q.lower()), auth=AWSAUTH, headers=HEADERS)
        response = response.json()
        print("Response: {}".format(response))
        if len(response['hits']['hits']) == 0:
            print("No photographs found matching the query: {}".format(q))
            continue
        
        query_photos = [{
            'objectKey': sample['_source']['objectKey'],
            'bucket': sample['_source']['bucket'],
            'createdTimestamp': sample['_source']['createdTimestamp'],
            'labels': sample['_source']['labels']
        } for sample in response['hits']['hits']]
        print("Query: {} Photos: {}".format(q, query_photos))
        photos = photos + query_photos
    
    seen_keys, dedup_photos = [], []
    for p in photos:
        if p['objectKey'] in seen_keys:
            continue
        dedup_photos.append(p)
        seen_keys.append(p['objectKey'])
    return send_response(dedup_photos)
