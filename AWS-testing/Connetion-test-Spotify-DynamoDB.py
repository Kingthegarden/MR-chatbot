import json,os
import requests
import base64
import logging
import time
import pymysql
import boto3
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client_id = ""
client_secret = ""

rds_host = ''
rds_user ='admin'
rds_pwd = ''
rds_db = 'musicdb'

try:
    conn = pymysql.connect(host=rds_host, user=rds_user, password=rds_pwd, db=rds_db)
    cursor = conn.cursor()

    dynamodb = boto3.resource('dynamodb',region_name='us-east-2') 
    table=dynamodb.Table('artist_toptracks') #dynanoDB 파티션키 : track_id

except:
    logging.error('could not connect to rds or dynamodb')

# 스포티파이(top-tracks API)를 통해 아티스트 음악정보 수집,변형,Dynamodb 저장
def get_toptracks_api(artist_id,headers):
    endpoint = "https://api.spotify.com/v1/artists/{}/top-tracks".format(artist_id)

    query_params = {'market':'KR'}
    ## 헤더에 token을 넣은 get방식으로 메세지 요청
    artist_t=requests.get(endpoint,params=query_params,headers=headers)
    artist_tr=json.loads(artist_t.text)
    logging.info("API를 통해 top-trackss 데이터수집")
    #print(artist_tr)

    ## 안정적인 데이터수집을 위한 API호출 예외처리
    if artist_t.status_code!=200:
        logging.error(json.loads(artist_t.text))

        # too much request일 경우, retry-After 시간(초)만큼 대기 후 재요청
        if artist_t.status_code == 429:
            retry_afer = json.loads(artist_t.headers)['retry-After']
            time.sleep(int(retry_afer))
            search_r=requests.get(endpoint,params=query_params,headers=headers)
        # API 인증키 만료일 경우, token다시 가져옴
        elif artist_t.code==401:
            search_r=requests.get(endpoint,params=query_params,headers=headers)
        # 이외의 예외상황
        else:
            logging.error(json.loads(artist_t.text))
    
    #Dynamodb작업
    for track in artist_tr['tracks']:
        data={
            'track_id': track['id'],
            'artist_id':artist_id,
            'artist_name':track['artists'][0]['name'],
            'track_name': track['name'],
            'track_url': track['external_urls']['spotify'],
            'album':{
                'album_id': track['album']['id'],
                'album_name': track['album']['name'],
                'album_type': track['album']['album_type'],
                'album_image': track['album']['images'][0]['url'],
                'release_date': track['album']['release_date'],
                'total_tracks': track['album']['total_tracks']
            }
        }
        table.put_item(Item=data)
    
    logging.info("신규 아티스트의 음악정보 dynamodb insert완료")

# DynamoDB에서 아티스트 음악정보 쿼리
def get_toptracks_db(id):
    # 파티션키가 아닌 컬럼으로 조회하기 위해 query 대신 scan사용
    select_result = table.scan(FilterExpression = Attr('artist_id').eq(id))
    logging.info("Dynamodb에서 top-tracks 조회결과")
    #print(select_result)

    #최근 발매된 앨범순으로 정렬
    select_result['Items'].sort(key=lambda x: x['album']['release_date'], reverse=True)
    items = []
    for track in select_result['Items'][:3]: #최근 발매된 3개의 데이터만 가져오기

        # ListCard의 item형태에 맞게 변형
        temp_dic = {
            "title": track['track_name'], #타이틀곡명
            "description": track['album']['release_date'], #발매일
            "imageUrl": track['album']['album_image'], #앨범커버이미지
            "link": {
                "web": track['track_url'] #스포티파이링크
            }
        }
        items.append(temp_dic)

    return items

# 스포티파이(search API)를 통해 artist_id 리턴
def get_artist_api(artist_name,headers):
    endpoint = "https://api.spotify.com/v1/search"
    query_params = {'q':artist_name,'type':'artist','limit':'1'}

    ## 헤더에 token을 넣은 get방식으로 메세지 요청
    search_r=requests.get(endpoint,params=query_params,headers=headers)
    search_ar=json.loads(search_r.text)
    logger.info("API를 통해 artist 데이터수집")
    #print(search_ar)

    ## 안정적인 데이터수집을 위한 API호출 예외처리
    if search_r.status_code!=200:
        logging.error(json.loads(search_r.text))

        # too much request일 경우, retry-After 시간(초)만큼 대기 후 재요청
        if search_r.status_code == 429:
            retry_afer = json.loads(search_r.headers)['retry-After']
            time.sleep(int(retry_afer))
            search_r=requests.get(endpoint,params=query_params,headers=headers)
        # API 인증키 만료일 경우, token다시 가져옴
        elif search_r.code==401: #get token again
            search_r=requests.get(endpoint,params=query_params,headers=headers)
        # 이외의 예외상황
        else:
            logging.error(json.loads(search_r.text))

    # RDS작업
    artist_item= search_ar['artists']['items'][0]

    # mysql에 insert row 저장
    artist_data ={
        'artist_id' : artist_item['id'],
        'artist_name' : artist_item['name'],
        'popularity' : artist_item['popularity'],
        'followers' : artist_item['followers']['total'],
        'artist_url' : artist_item['external_urls']['spotify'],
        'image_url' : artist_item['images'][0]['url'],
    }
    # insert_row(cursor,artist_data,'artists')
    # conn.commit()
    # logging.info("신규 아티스트정보 RDS insert완료")

    return artist_data['artist_id']

def get_header():
    endpoint = "https://accounts.spotify.com/api/token"

    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode('utf-8')).decode('ascii')
    headers = {"Authorization": "Basic {}".format(encoded)}
    payload = {"grant_type": "client_credentials"}
    # POST방식으로 access_token을 요청
    response = requests.post(endpoint, data=payload, headers=headers)
    access_token = json.loads(response.text)['access_token']
    headers = {"Authorization": "Bearer  {}".format(access_token)}

    return headers

artist_id = get_artist_api('BTS', get_header()) #아티스트정보 리턴
get_toptracks_api(artist_id, get_header()) #음악정보 DynamoDB 저장