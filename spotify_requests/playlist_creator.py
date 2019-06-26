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

    def create_playlist(self, time_range, tracks, playlist_name, playlist_description):
        """
        Main function of this class. Creates a playlist given time range and top tracks.
        """
        playlist_exists = self._check_playlist_exists(playlist_name)   # write over playlist if it already exists. currently doesn't work because the playlist doesn't show up when getting user's playlists.
        if playlist_exists:
            return self._override_playlist(playlist_exists, tracks)
        body = json.dumps({'name': playlist_name, 'description': playlist_description, 'public': False})
        r = requests.post(self.url, verify=True, headers=self.headers, data=body)
        if r.status_code // 100 == 2:    # check if response is some kind of 200
            playlist_id = self._handle_response(r)
        else:
            print(r.status_code)
            playlist_id = 0
            return False

        fill_playlist = self._add_songs_to_playlist(playlist_id, tracks)
        return True if fill_playlist else False

    def _handle_response(self, r):
        """
        Handles JSON data and just returns id of playlist
        """
        r = json.loads(r.text)
        return r['id']

    def _add_songs_to_playlist(self, playlist_id, tracks):
        """
        Given playlist id and list of tracks, adds songs to a playlist
        """
        add_tracks_url = self.playlists_url.format(playlist_id)
        track_uris = [track['uri'] for track in tracks]
        body = json.dumps({'uris': track_uris})
        r = requests.post(add_tracks_url, verify=True, headers=self.headers, data=body)
        print("ADD SONGS TO PLAYLIST STATUS CODE: " + str(r.status_code))
        if r.status_code // 100 == 2:
            return True
        return False

    def _check_playlist_exists(self, playlist_name):
        """
        Given a name, checks if a user has a certain playlist
        """
        playlists = self._get_user_playlists()
        playlist_titles = [playlist['name'] for playlist in playlists['items']]
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                print(playlist['name'])
                return playlist['id']
        return False

    def _override_playlist(self, playlist_id, new_tracks):
        """
        Updates a user's playlist. Deletes all old tracks and replaces with new tracks.
        """
        # get old playlist tracks
        get_playlist_tracks_url = self.playlists_url.format(playlist_id)
        r = requests.get(get_playlist_tracks_url, verify=True, headers=self.headers)
        tracks = json.loads(r.text)
        track_uris = [track['track']['uri'] for track in tracks['items']]
        uris = []
        for uri in track_uris:
            uris.append({'uri': uri})
        uris_dict = {'tracks': uris}
        # delete old playlist tracks
        body = json.dumps(uris_dict)
        delete_playlist_tracks_url = self.playlists_url.format(playlist_id)
        r = requests.delete(delete_playlist_tracks_url, verify=True, headers=self.headers, data=body)
        print("DELETE OLD PLAYLIST TRACKS STATUS CODE: " + str(r.status_code))
        # add new playlist tracks
        return self._add_songs_to_playlist(playlist_id, new_tracks)

    def _get_user_playlists(self):
        """
        Gets a list of a user's playlists
        """
        get_playlists_url = self.user_playlists_url.format(self.user_id)
        r = requests.get(get_playlists_url, verify=True, headers=self.headers)
        if r.status_code // 100 == 2:
            playlists = json.loads(r.text)
            return playlists
        else:
            return None
