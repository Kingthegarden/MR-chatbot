import boto3

def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table('artist_toptracks')
    response = table.put_item(
        Item = {
            'track_id' : '23123123',
            'album' : '{"album_id" : "sdfsd"}',
            'artist_id' : 'DBS123',
            'artist_name' : 'JW',
            'track_name' : 'JWsong'
        }
    )
    return response