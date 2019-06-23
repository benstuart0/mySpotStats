# -*- coding: utf-8 -*-
import sys
import requests
import json

class PlaylistCreator:
    """
    Class for creating playlist of loaded tracks
    """
    def __init__(self, header, user):
        self.playlists_url = 'https://api.spotify.com/v1/playlists/{}/tracks'
        self.user_playlists_url = 'https://api.spotify.com/v1/users/{}/playlists'
        self.token = header
        self.user_id = user['id']
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}
        self.url = 'https://api.spotify.com/v1/users/{}/playlists'.format(self.user_id)

    def create_playlist(self, time_range, tracks):
        playlist_name = "My Top Tracks of " + time_range
        #playlist_exists = self._check_playlist_exists(playlist_name)
        #if playlist_exists:
            #return self._override_playlist(playlist_exists, tracks)
        playlist_description = "My 99 most listened to tracks of " + time_range
        body = json.dumps({'name': playlist_name, 'description': playlist_description, 'public': False})
        r = requests.post(self.url, verify=True, headers=self.headers, data=body)
        if r.status_code // 100 == 2:    # check if response is some kind of 200
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
        add_tracks_url = self.playlists_url.format(playlist_id)
        track_uris = [track['uri'] for track in tracks]
        body = json.dumps({'uris': track_uris})
        r = requests.post(add_tracks_url, verify=True, headers=self.headers, data=body)
        if r.status_code // 100 == 2:
            return True
        return False

    def _check_playlist_exists(self, playlist_name):
        playlists = self._get_playlists()
        playlist_titles = [playlist['name'] for playlist in playlists['items']]
        import pdb; pdb.set_trace()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return playlist['id']
        return False

    def _override_playlist(self, playlist_id, new_tracks):
        print("YOURE STARTING TO OVERRIDE PLAYLIST BOIIIIi")
        # get old playlist tracks
        get_playlist_tracks_url = self.playlists_url.format(playlist_id)
        r = requests.get(get_playlist_tracks_url, verify=True, headers=headers)
        tracks = json.loads(r.text)
        track_uris = [track['uri'] for track in tracks]
        # delete old playlist tracks
        body = {'tracks':track_uris}
        delete_playlist_tracks_url = self.playlists_url.format(playlist_id)
        r = requests.delete(delete_playlist_tracks_url, verify=True, headers=headers, data=body)
        # add new playlist tracks
        new_track_uris = [track['uri'] for track in new_tracks]
        body = {'tracks':new_track_uris}
        add_tracks_to_playlist_url = self.playlists_url.format(playlist_id)
        r = requests.post(self.playlists_url, verify=True, headers=headers, data=body)
        print("YOU JUSt oVERRODE THE PLAYLIST BOII")
        return True

    def _get_playlists(self):
        get_playlists_url = self.user_playlists_url.format(self.user_id)
        r = requests.get(get_playlists_url, verify=True, headers=self.headers)
        if r.status_code // 100 == 2:
            playlists = json.loads(r.text)
            return playlists
        else:
            return None

    def handle_response(self, r):
        r = json.loads(r.text)
        id = r['id']
        return id
