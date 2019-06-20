import boto3
from spotify_requests.track import TrackGrabber
from spotify_requests.artist import ArtistGrabber
import json
from decimal import Decimal

dynamoDB = boto3.resource('dynamodb')
table = dynamoDB.Table('spotify-user-top-songs')

def update_db(user, auth_header):
    tracks = get_tracks(auth_header)
    tracks = json.loads(json.dumps(tracks), parse_float=Decimal)
    artists = get_artists(auth_header)
    artists = json.loads(json.dumps(artists), parse_float=Decimal)

    table.put_item(Item={
        'user_id': user['id'],
        'user_uri': user['uri'],
        'user_email': user['email'],
        'user_country': user['country'],
        'short_term_tracks': tracks['short_term'],
        'medium_term_tracks': tracks['medium_term'],
        'long_term_tracks': tracks['long_term'],
        'short_term_artists': artists['short_term'],
        'medium_term_artists': artists['medium_term'],
        'long_term_artists': artists['long_term']
    }
)

def get_tracks(auth_header):
    tg = TrackGrabber(auth_header)
    short_term = tg.main('short_term',49,0) + tg.main('short_term',50,49)
    medium_term = tg.main('medium_term',49,0) + tg.main('medium_term',50,49)
    long_term = tg.main('long_term',49,0) + tg.main('long_term',50,49)
    tracks = {
        'short_term': short_term,
        'medium_term': medium_term,
        'long_term': long_term
    }
    return tracks

def get_artists(auth_header):
    ag = ArtistGrabber(auth_header)
    short_term = ag.main('short_term',49,0) + ag.main('short_term',50,49)
    medium_term = ag.main('medium_term',49,0) + ag.main('medium_term',50,49)
    long_term = ag.main('long_term',49,0) + ag.main('long_term',50,49)
    artists = {
        'short_term': short_term,
        'medium_term': medium_term,
        'long_term': long_term
    }
    return artists
