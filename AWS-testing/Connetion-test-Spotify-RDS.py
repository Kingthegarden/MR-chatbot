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

    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    table=dynamodb.Table('artist_toptracks') #dynanoDB 파티션키 : track_id
except:
    logging.error('could not connect to rds or dynamodb')


# 스포티파이(search API)를 통해 아티스트 정보 수집,변형,RDS 저장
def get_artist_api(artist_name,headers):
    endpoint = "https://api.spotify.com/v1/search"
    query_params = {'q':artist_name,'type':'artist','limit':'1'}
    
    ## 헤더에 token을 넣은 get방식으로 메세지 요청
    search_r=requests.get(endpoint,params=query_params,headers=headers)
    search_ar=json.loads(search_r.text)
    logger.info("API를 통해 artist 데이터수집")

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
    insert_row(cursor,artist_data,'artists')
    conn.commit()
    logging.info("신규 아티스트정보 RDS insert완료")

    return artist_data['artist_id']

# 신규 아티스트 정보를 mysql에 insert하는 함수
def insert_row(cursor,data,table):

    # sql 쿼리문은 아래와 같은 형태
    '''
    INSERT INTO artists ( artist_id, artist_name, followers, popularity, artist_url, image_url )
    VALUES ( %s, %s, %s, %s, %s, %s )
    ON DUPLICATE KEY UPDATE artist_id=values(artist_id), artist_name=values(artist_name), followers=values(followers),
    popularity=values(popularity), artist_url=values(artist_url), image_url=values(image_url)
    '''

    placeholders = ', '.join(['%s'] * len(data)) # %s, %s, %s, %s, %s, %s
    columns = ', '.join(data.keys())
    key_placeholders = ', '.join(['{0}=values({0})'.format(k) for k in data.keys()])

    sql = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLICATE KEY UPDATE %s" % (table, columns, placeholders, key_placeholders)

    cursor.execute(sql, list(data.values()))

# Spotify API연결을 위한 Token을 가져옴
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
    
# 스포티파이(search API)를 통해 아티스트 정보 수집,변형,RDS 저장
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
    insert_row(cursor,artist_data,'artists')
    conn.commit()
    logging.info("신규 아티스트정보 RDS insert완료")

    return artist_data['artist_id']

# get_artist_api('BTS', get_header())
