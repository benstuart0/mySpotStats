# -*- coding: utf-8 -*-
import sys
import requests
import json

class TrackGrabber:
    def __init__(self, header):
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}
        self.url_base = 'https://api.spotify.com/v1/me/top/tracks'
        self.audio_features_base = 'https://api.spotify.com/v1/audio-features?ids='
        self.time_range = 'medium_term'
        self.limit = 10
        self.offset = 0

    def main(self, time_range='medium_term', limit=10, offset=0):
        self.time_range = time_range
        self.limit = limit
        self.offset = offset
        url = self.url_base + '?time_range=%s&limit=%s&offset=%s' % (self.time_range, self.limit, self.offset)
        print(url)
        print(self.headers)
        r = requests.get(url, verify=True, headers=self.headers)
        if str(r) == '<Response [200]>':
            tracks = self.handle_response(r)
        else:
            print(str(r))
            tracks = None
            exit()
        return tracks

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

    def translate_key(self, key, mode):
        result = ''
        if mode == 1:
            mode = ' Major'
        if mode == 0:
            mode = ' Minor'
        if key == 0:
            pitch = 'C'
        if key == 1:
            pitch = 'C#'
        if key == 2:
            pitch = 'D'
        if key == 3:
            pitch = 'Eb'
        if key == 4:
            pitch = 'E'
        if key == 5:
            pitch = 'F'
        if key == 6:
            pitch = 'F#'
        if key == 7:
            pitch = 'G'
        if key == 8:
            pitch = 'Ab'
        if key == 9:
            pitch = 'A'
        if key == 10:
            pitch = 'Bb'
        if key == 11:
            pitch = 'B'
        return pitch + mode


    def get_audio_features(self, ids):
        track_features = []
        url = self.audio_features_base + ids[0]
        ids.pop(0)
        for id in ids:
            url = url + ',%s' % id
        r = requests.get(url, verify=True, headers=self.headers)
        if str(r) == '<Response [200]>':
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
        tracks = []
        r = json.loads(r.text)
        items = r['items']
        term = self.get_term(range)
        i = int(self.offset) + 1
        track_ids = [song['id'] for song in items]
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
                'speechiness': audio_features['speechiness']
            }
            tracks.append(track_obj)
            i += 1
        return tracks

    def display_tracks(self, tracks):
        toReturn = ""
        for track in tracks:
            toReturn += ("%s. %s - %s \\\\ %s\n" % (track['index'],track['title'],track['artist'],track['key']))
        return toReturn

    def get_stats(self, tracks):
        toReturn = ""
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
        #toReturn += ("\nDANCE: %s\nVALENCE: %s\nENERGY: %s\nDURATION: %s\nSPEECHINESS: %s\n"% (stats['ave_danceability'],stats['ave_valence'],stats['ave_energy'],stats['ave_duration'], stats['ave_speechiness']))
        return stats
