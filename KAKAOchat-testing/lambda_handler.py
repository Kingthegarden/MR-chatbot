import json

def lambda_handler(event, context):

    # 메시지 내용은 request의 ['body']에 들어 있음
    request_body = json.loads(event['body'])
    params = request_body['action']['params']
    solo = params['solo'] # 솔로 아티스트 파라미터 생기는지 테스트

    result = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "요청한 아티스트는 {}입니다.".format(solo)
                    }
                }
            ]
        }
    }

    return {
        'statusCode':200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        }
    }