# -*- coding: utf-8 -*-
import sys
import requests
import json

MODES = {
    0: ' Minor',
    1: ' Major'
}

KEYS = {
    0: 'C',
    1: 'Db',
    2: 'D',
    3: 'Eb',
    4: 'E',
    5: 'F',
    6: 'Gb',
    7: 'G',
    8: 'Ab',
    9: 'A',
    10: 'Bb',
    11: 'B'
}

class TrackGrabber:
    """
    Class for making requests to load tracks onto track pages
    """
    def __init__(self, header):
        self.modes = MODES
        self.keys = KEYS
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}
        self.url_base = 'https://api.spotify.com/v1/me/top/tracks'
        self.audio_features_base = 'https://api.spotify.com/v1/audio-features?ids='
        self.time_range = 'medium_term'
        self.limit = 10
        self.offset = 0

    def main(self, time_range='medium_term', limit=10, offset=0):
        """
        Makes request to retrieve user's top tracks in certain timeframe
        """
        self.time_range = time_range
        self.limit = limit
        self.offset = offset
        url = self.url_base + '?time_range=%s&limit=%s&offset=%s' % (self.time_range, self.limit, self.offset)
        r = requests.get(url, verify=True, headers=self.headers)
        if str(r) == '<Response [200]>':
            tracks = self.handle_response(r)
        else:
            print(str(r))
            tracks = None
            exit()
        return tracks

    def get_pop_rating(self, avePop):
        """
        Uses the average popularity of the artists to give a verdict on your overall taste in music.
        """
        if avePop < 40:
            return 'Your music tastes are obscure.'
        if avePop < 50:
            return "Fuck you."
        else:
            return "You basic bitch."

    def translate_key(self, key, mode):
        key = self.keys[key]
        mode = self.modes[mode]
        return key + mode


    def get_audio_features(self, ids):
        """
        Retrieves audio features of a track
        """
        track_features = []
        url = self.audio_features_base + ids[0]
        ids.pop(0)
        for id in ids:
            url = url + ',%s' % id
        r = requests.get(url, verify=True, headers=self.headers)
        if r.status_code // 100 == 2:
            audio_features_list = json.loads(r.text)
            for audio_features in audio_features_list['audio_features']:
                if audio_features:
                    key = self.translate_key(audio_features['key'],audio_features['mode'])
                    audio_features = {
                        'key': key,
                        'valence':audio_features['valence'],
                        'energy':audio_features['energy'],
                        'danceability':audio_features['danceability'],
                        'speechiness': audio_features['speechiness']
                    }
                else:
                    key = 'No Key'
                    audio_features = {
                        'key': key,
                        'valence': 0,
                        'energy': 0,
                        'danceability': 0,
                        'speechiness': 0
                    }
                track_features.append(audio_features)
        else:
            return None

        return track_features

    def handle_response(self, r):
        """
        Unpacks JSON list of tracks to make it easier to use
        """
        tracks = []
        r = json.loads(r.text)
        items = r['items']
        i = int(self.offset) + 1
        track_ids = [song['id'] for song in items]
        if len(track_ids) == 0:
            return []
        track_audio_features = self.get_audio_features(track_ids)
        for index, item in enumerate(items):
            songTitle = item['name']
            artistName = item['artists'][0]['name']
            duration = int(item['duration_ms']) / 1000
            audio_features = track_audio_features[index]
            track_obj = {
                'index': i,
                'title':songTitle,
                'artist':artistName,
                'popularity':item['popularity'],
                'spotify_id':item['id'],
                'duration':duration,
                'key': audio_features['key'],
                'valence': audio_features['valence'],
                'energy': audio_features['energy'],
                'danceability': audio_features['danceability'],
                'speechiness': audio_features['speechiness'],
                'uri': item['uri']
            }
            tracks.append(track_obj)
            i += 1
        return tracks


    def get_stats(self, tracks):
        """
        Gets ultimate stats on tracks (displayed at bottom of page). Could be updated to make more readable
        """
        danceability = [track['danceability'] for track in tracks]
        valence = [track['valence'] for track in tracks]
        energy = [track['energy'] for track in tracks]
        duration = [track['duration'] for track in tracks]
        speechiness = [track['speechiness'] for track in tracks]
        stats = {
            'ave_danceability': sum(danceability) / len(danceability),
            'ave_valence': sum(valence) / len(valence),
            'ave_energy': sum(energy) / len(energy),
            'ave_duration': sum(duration) / len(duration),
            'ave_speechiness': sum(speechiness) / len(speechiness)
        }
        return stats
