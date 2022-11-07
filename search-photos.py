import boto3
import requests

AWS_AUTH = ('master', 'Columbia110x3$')
HEADERS = { "Content-Type": "application/json" }
SLOT_KEY_1 = 'Keyword1'
SLOT_KEY_2 = 'Keyword2'
OPEN_SERVICE_URL = 'https://search-photos-ctm5peqt7woxp4qzhpvenm3p7y.us-east-1.es.amazonaws.com_search?q=labels:{}'

def lambda_handler(event, context):
    print("Event: {}".format(event))
    
    userMessage = event["message"]
    client = boto3.client("lexv2-runtime")
    response = client.recognize_text(
        botId='OIZMTO0GTX',
        botAliasId='QPY5ZFCKA9',
        localeId='en_US',
        sessionId='sb4539',
        text=userMessage
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
    
    photos = []
    for q in queries:
        response = requests.get(OPEN_SERVICE_URL.format(q), auth=AWSAUTH, headers=HEADERS)
        response = response.json()
        
        samples = []
        if len(response['hits']['hits']) == 0:
            print("No photographs found matching the query: {}".format(q))
            continue
        
        query_photos = [{
            'id': sample['_source']['id'],
            'cuisine': sample['_source']['cuisine']
        } for sample in samples]
        print("Query Photos: {}".format(query_photos))
        photos = photos + query_photos
    
    photos = list(set(photos))
    return photos