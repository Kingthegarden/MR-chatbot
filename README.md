# 음악추천챗봇과 AWS 데이터파이프라인
<hr>

전체적인 진행과정은 노션에서 확인할 수 있습니다: https://onyx-bandicoot-bec.notion.site/27f27db408014a1c84c66aa6d78ddeab <br>

## 개요
Spotify(음원서비스)API를 활용해 음원데이터를 수집하고 <br>
유저가 아티스트를 입력하면 유사한 아티스트와 노래를 추천해주는 AWS Serverelss기반 카카오톡 챗봇 개발

## 프로젝트 기간 
2022.01.03 ~ 2022.01.30

## 사용기술
- Language : Python 3.8 <br>
- DB : AWS RDS(MySQL), AWS DynamoDB, AWS S3<br>
- Infra : AWS Lambda, API Gateway, AWS Athena<br>
- API : Spotify API, Kakao i Open Builder

## 수행역할 
AWS를 사용한 데이터 수집·저장·처리 그리고 유사도 분석까지 자동화된 데이터 파이프라인 개발
- Python & Spotify API를 통해 아티스트의 데이터수집
- 데이터 전처리 후 AWS RDS 및 AWS DynamoDB에 데이터저장 
- raw 데이터와 Spotify의 음악 메타데이터를 AWS S3에 저장하여 DataLake 구현
- AWS Athena를 통해 유사도를 계산하고, Mysql에 저장하여 DataMart로 활용
- 입력한 아티스트 정보 및 관련 아티스트·음악정보를 추천할 수 있는 Serverless 카카오톡 챗봇 서비스 개발

## 아키텍쳐  
### AWS API Gateway와 AWS Lambda기반의 Serverless 구조

![serverelss2](images/serverless_2.PNG)

- 사용자가 챗봇에게 아티스트를 입력하면 API Gateway가 트리거가 되어 lambda 함수가 호출
- 챗봇이 API Gateway를 거쳐 POST 방식으로 보낸 request 메세지를 lambda가 받아 처리한다.   
- 사용자의 Request가 있을때만 동작하여 합리적인 비용으로 서비스 운영가능
- 별도의 서버를 관리할 필요 없이 lambda function 호출 및 배포 가능 <br>


## 데이터파이프라인 
### S3, Athena, boto3 등을 활용한 AWS기반의 데이터 파이프라인 

![datapipline](images/datapipeline_2.PNG)

- Spotify API에서 수집한 raw 데이터와 RDS, DynamoDB에 저장되어 있던 데이터를 S3로 모아 DataLake 구현 
- 대화형 쿼리엔진 Athena를 사용하여 쿼리수행 후 유사도 분석 결과를 별도로 저장하여 데이터 마트 구현

## 코드리뷰 및 스크립트 설명 

### 1. lambda_function.py
#### Spotify API를 기반으로 데이터를 수집하고, 저장하여 카카오톡 메세지 형태로 응답해주는 로직처리 <br>

![Untitled (1)](https://user-images.githubusercontent.com/78723318/123921481-007ce500-d9c2-11eb-9694-87b4d694c9a5.png)
![Untitled (2)](https://user-images.githubusercontent.com/78723318/123921519-0bd01080-d9c2-11eb-9283-7d0b966fb0db.png)

- 기존 아티스트를 받았을 경우, DynamoDB와 RDS에서 데이터를 조회하여 카카오톡 메세지 형태로 응답
- 신규 아티스트를 받았을 경우, Spotify API를 통해 관련 데이터 수집 및 저장 
- AWS RDS : 아티스트 데이터(artists), AWS DynamoDB : 아티스트의 음악정보 데이터(top_track) 저장

### 2. S3_Datalake.py
#### raw 데이터를 parquet 포맷으로 압축하여 S3에 저장하는 로직처리 → DataLake 구현 <br>

![Untitled (3)](https://user-images.githubusercontent.com/78723318/123921987-8ac54900-d9c2-11eb-998f-46ce5d1c4a64.png)

- AWS RDS에 저장된 artist_id 로 Spotify API를 통해 raw 데이터 수집
- S3에 저장하기 위해 계층형 구조의 raw 데이터를 flat한 형태로 변형
- 컬럼기반 포맷(parquet)으로 압축된 데이터를 S3 저장

### 3. Athena_data.py
#### Athena 쿼리수행 및 아티스트 간 유사도를 계산하여 RDS에 저장하는 로직처리 → DataMart 구성 <br>

![캡처](https://user-images.githubusercontent.com/78723318/124017992-57b2a200-da22-11eb-8a14-51eca5b16202.PNG)

- S3에 저장된 데이터를 대상으로 AWS Athena 쿼리를 수행하여 구조화된 데이터로 변환 
- 아티스트별 평균 음악 메타데이터를 Euclidean Distance 알고리즘 기반으로 유사도 계산
- 아티스트간의 거리가 가까운 (유사도가 높은) 아티스트를 RDS에 저장

## 프로젝트 결과 
1. 신규 아티스트 입력결과 : 유저가 입력한 아티스트와 노래정보 전달

![사례1 분석중](https://user-images.githubusercontent.com/78723318/124323880-fb37ba00-dbbc-11eb-86ac-c511dfb9a8e7.PNG)

2. 기존 아티스트 입력결과 : 유저가 입력한 아티스트 정보를 바탕으로 데이터처리 및 분석결과 (가장 유사한 아티스트의 노래정보) 전달 <br>

![사례2 분석결과](https://user-images.githubusercontent.com/78723318/124323992-291cfe80-dbbd-11eb-9abc-7be9b5ff6835.PNG)
