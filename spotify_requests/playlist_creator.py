# -*- coding: utf-8 -*-
import sys
import requests
import json

add_tracks_to_playlist_url = 'https://api.spotify.com/v1/playlists/{}/tracks'

class PlaylistCreator:
    def __init__(self, header,user):
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}
        self.url = 'https://api.spotify.com/v1/users/{}/playlists'.format(user['id'])

    def create_playlist(self, time_range, tracks):
        playlist_name = "My Top Tracks of " + time_range
        playlist_description = "My 99 most listened to tracks of " + time_range
        body = json.dumps({'name': playlist_name, 'description': playlist_description, 'public': False})
        r = requests.post(self.url, verify=True, headers=self.headers, data=body)

        if r.status_code < 300:    # check if response is some kind of 200
            playlist_id = self.handle_response(r)
        else:
            print(str(r))
            playlist_id = 0
            return False

        fill_playlist = self._add_songs_to_playlist(playlist_id, tracks)
        if fill_playlist:
            return True
        return False

    def _add_songs_to_playlist(self, playlist_id, tracks):
        add_tracks_url = add_tracks_to_playlist_url.format(playlist_id)
        track_uris = [track['uri'] for track in tracks]
        body = json.dumps({'uris': track_uris})
        r = requests.post(add_tracks_url, verify=True, headers=self.headers, data=body)
        if r.status_code < 300:
            return True
        return False

    def _remove_old_playlist(self, playlist_name):

        return 1

    def handle_response(self, r):
        r = json.loads(r.text)
        id = r['id']
        return id
