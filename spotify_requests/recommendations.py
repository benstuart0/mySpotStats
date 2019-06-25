import json
import requests

class Recommendations:
    def __init__(self, header):
        self.url_base = 'https://api.spotify.com/v1/recommendations'
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}

    def get_recommendations(self, artists=[], tracks=[]):
        playlist_name = "My Spot Stats Recommended Songs"
        playlist_description = "Songs recommended by mySpotStats algorithm."
        # query_string = '?seed_artists='
        # for artist in artists:
        #     query_string += artist['id']
        #     query_string += ','
        # query_string = query_string[:-1]    # delete comma from query
        query_string = '?seed_tracks='
        for track in tracks:
            query_string += track['spotify_id']
            query_string += ','
        query_string = query_string[:-1]    # delete last comma again
        url = self.url_base + query_string
        r = requests.get(url, verify=True, headers=self.headers)
        if r.status_code // 100 == 2:
            recommended_tracks = self._handle_response(r)
            return recommended_tracks
        else:
            print("Recommendations Request Status Code: " + str(r.status_code))
            exit()

    def _handle_response(self, r):
        r = json.loads(r.text)
        tracks = r['tracks']
        return tracks
