import requests
import base64
import json
import Search
import Artist

client_id = ""
client_secret = ""

endpoint = "https://accounts.spotify.com/api/token"

encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode('utf-8')).decode('ascii')
headers = {"Authorization": "Basic {}".format(encoded)}
payload = {"grant_type": "client_credentials"}
response = requests.post(endpoint, data=payload, headers=headers)
access_token = json.loads(response.text)['access_token']

headers = {"Authorization": "Bearer  {}".format(access_token)}

#1.search artist (with search api)
search_data = Search.artist('BTS', headers)['artists']

for item in search_data['items']:
    #print(item.keys())
    artist_id = item['id']
    artist_name = item['name']
    popularity = item['popularity']
    followers = item['followers']['total']
    artist_url = item['external_urls']['spotify']
    artist_image = item['images'][0]['url']
    genres= item['genres']

#1.1 insert DB(RDS:mysql)

#2.search top track
    artist_track = Artist.top_tracks(artist_id, headers)['tracks']
    for item in artist_track:
        track_id = item['id']
        track_name = item['name']
        album = item['album'] #{}
        artist = item['artists'] #[]
        track_url = item['external_urls']['spotify']
        if 'images' in item:
            track_images = item['images'][0]['url']
    print(artist_track)



    #{'album': {'album_type': 'album', 
    # 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/4gzpq5DPGxSnKTe4SA8HAU'}, 
    # 'href': 'https://api.spotify.com/v1/artists/4gzpq5DPGxSnKTe4SA8HAU', 'id': '4gzpq5DPGxSnKTe4SA8HAU',
    #  'name': 'Coldplay', 'type': 'artist', 'uri': 'spotify:artist:4gzpq5DPGxSnKTe4SA8HAU'}], 
    # 'external_urls': {'spotify': 'https://open.spotify.com/album/06mXfvDsRZNfnsGZvX2zpb'}, 
    # 'href': 'https://api.spotify.com/v1/albums/06mXfvDsRZNfnsGZvX2zpb', 'id': '06mXfvDsRZNfnsGZvX2zpb', 
    # 'images': [{'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273ec10f247b100da1ce0d80b6d', 'width': 640}, {'height': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e02ec10f247b100da1ce0d80b6d', 'width': 300}, {'height': 64, 'url': 'https://i.scdn.co/image/ab67616d00004851ec10f247b100da1ce0d80b6d', 'width': 64}], 'name': 'Music Of The Spheres', 'release_date': '2021-10-15', 'release_date_precision': 'day', 'total_tracks': 12, 'type': 'album', 'uri': 'spotify:album:06mXfvDsRZNfnsGZvX2zpb'}, 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/4gzpq5DPGxSnKTe4SA8HAU'}, 'href': 'https://api.spotify.com/v1/artists/4gzpq5DPGxSnKTe4SA8HAU', 'id': '4gzpq5DPGxSnKTe4SA8HAU', 'name': 'Coldplay', 'type': 'artist', 'uri': 'spotify:artist:4gzpq5DPGxSnKTe4SA8HAU'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/3Nrfpe0tUJi4K4DXYWgMUX'}, 'href': 'https://api.spotify.com/v1/artists/3Nrfpe0tUJi4K4DXYWgMUX', 'id': '3Nrfpe0tUJi4K4DXYWgMUX', 'name': 'BTS', 'type': 'artist', 'uri': 'spotify:artist:3Nrfpe0tUJi4K4DXYWgMUX'}], 'disc_number': 1, 'duration_ms': 226198, 'explicit': False, 'external_ids': {'isrc': 'GBAYE2100952'}, 'external_urls': {'spotify': 'https://open.spotify.com/track/46HNZY1i7O6jwTA7Slo2PI'}, 'href': 'https://api.spotify.com/v1/tracks/46HNZY1i7O6jwTA7Slo2PI', 'id': '46HNZY1i7O6jwTA7Slo2PI', 'is_local': False, 'is_playable': True, 'name': 'My Universe', 'popularity': 87, 'preview_url': 'https://p.scdn.co/mp3-preview/5da74c03a1f17ed58315050022c1452fb431a2ad?cid=13b0455fa25e466b84e581503350d4b5', 'track_number': 10, 'type': 'track', 'uri': 'spotify:track:46HNZY1i7O6jwTA7Slo2PI'}