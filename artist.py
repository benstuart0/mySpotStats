# -*- coding: utf-8 -*-
import sys
import requests
import json

class ArtistGrabber:
    def __init__(self, token):
        self.token = token
        self.HEADERS = {'content-type': 'application/json', 'authorization': 'Bearer %s' % self.token}
        self.URL_BASE = 'https://api.spotify.com/v1/me/top/artists'
        self.AUDIO_FEATURES_BASE = 'https://api.spotify.com/v1/audio-features?ids='

    def main(self, time_range='medium_term', limit=10, offset=0):
        url = self.URL_BASE + '?time_range=%s&limit=%s&offset=%s' % (time_range, limit, offset)
        r = requests.get(url, verify=True, headers=self.HEADERS)
        if str(r) == '<Response [200]>':
            artists = handle_response(r)
        else:
            print (json.loads(r.text))
            artists = None
            exit()
        self.display_artists(artists)

    def get_term(self, range):
        if range == 'short_term':
            return 'the last 4 Weeks:'
        elif range == 'medium_term':
            return 'the last 6 Months:'
        elif range == 'long_term':
            return 'All Time:'

    def get_pop_rating(self, avePop):
        if avePop < 40:
            return 'Your music tastes are obscure.'
        if avePop < 50:
            return "Fuck you."
        else:
            return "You basic bitch."

    def handle_response(self, r):
        artists = []
        r = json.loads(r.text)
        items = r['items']
        term = self.get_term(range)
        i = int(offset) + 1
        artist_ids = [item['id'] for item in items]
        for index, item in enumerate(items):
            artist_name = item['name']
            artist_obj = {
                'index': i,
                'name':artist_name,
                'popularity':item['popularity'],
                'spotify_id':item['id'],
                'genres':item['genres']
                }
            artists.append(artist_obj)
            i += 1
        return artists

    def display_artists(self, artists):
        for artist in artists:
            print ("%s. %s \\\\ %s" % (artist['index'],artist['name'], artist['genres']))
