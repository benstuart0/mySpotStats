# -*- coding: utf-8 -*-
import sys
import requests
import json

class ArtistGrabber:
    """
    Class for making requests to load artists for artist pages
    """
    def __init__(self, header):
        self.token = header
        self.HEADERS = {'content-type': 'application/json', 'authorization': '%s' % self.token}
        self.URL_BASE = 'https://api.spotify.com/v1/me/top/artists'
        self.AUDIO_FEATURES_BASE = 'https://api.spotify.com/v1/audio-features?ids='

    def main(self, time_range='medium_term', limit=10, offset=0):
        """
        Class for making requests to load tracks onto track pages
        """
        self.time_range = time_range
        self.limit = limit
        self.offset = offset
        url = self.URL_BASE + '?time_range=%s&limit=%s&offset=%s' % (self.time_range, self.limit, self.offset)
        r = requests.get(url, verify=True, headers=self.HEADERS)
        if str(r) == '<Response [200]>':
            artists = self.handle_response(r)
        else:
            print(str(r))
            artists = None
            exit()
        return artists

    def get_pop_rating(self, artists):
        """
        Gets average popularity of top artists. Used to display verdict at bottom of artist pages.
        """
        total = 0
        counter = 0

        for artist in artists:
            total += int(artist['popularity'])
            counter += 1
        avePop = total / counter

        if avePop < 55:
            return 'Your music tastes are obscure.'
        if avePop < 65:
            return "Fuck you."
        else:
            return "You basic bitch."

    def handle_response(self, r):
        artists = []
        r = json.loads(r.text)
        items = r['items']
        i = int(self.offset) + 1
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
