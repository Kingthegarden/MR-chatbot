import json

def lambda_handler(event, context):

    try:

        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                handle_insert(record)
            elif record['eventName'] == 'MODIFY':
                handle_modify(record)
            elif record['eventName'] == 'REMOVE':
                handle_remove(record)
    except Exception as e:
        print(e)
        return "Ooops!"

def handle_insert(record):
    print('Handling INSERT event')
    
    newImage = record['dynamodb']['NewImage']
    newPlayerId = newImage['playerId']['S']

    print('New row added with playerId=' + newPlayerId)
    print('Done handling INSERT event')

def handle_modify(record):
    print('Handling MODIFY event')

    oldImage = record['dynamodb']['OldImage']
    oldScore = oldImage['score']['N']

    newImage = record['dynamodb']['NewImage']
    newScore = newImage['score']['N0']

    if oldScore != newScore:
        print('Scores changed - oldScore =' + str(oldScore + ', newScore=' + str(newScore)))
    
    print('Done hanling MODIFY event')

def handle_remove(record):
    print('Handling REMOVE event')

    oldImage = record['dynamodb']['OldImage']

    oldPlayerId = oldImage['playerId']['S']

    print('Row removed with playerId =' + oldPlayerId)
    print('Done hanling REMOVE event')