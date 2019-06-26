import json
import requests
import operator

class Recommendations:
    def __init__(self, header):
        self.url_base = 'https://api.spotify.com/v1/recommendations'
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}

    def get_recommendations(self, track_ids=[], artist_ids=[], genres=[]):
        """
        Gets list of recommended songs based on 5 seed values of artist, tracks, or genres
        """
        playlist_name = "My Spot Stats Recommended Songs"
        playlist_description = "Songs recommended by mySpotStats algorithm."
        query_string = '?seed_artists='

        for artist in artist_ids:
            query_string += artist
            query_string += ','
        query_string = query_string[:-1]    # delete comma from query

        #query_string += '&seed_tracks='
        # for track in track_ids:
        #     query_string += track
        #     query_string += ','
        # query_string = query_string[:-1]    # delete last comma again
        # query_string += '&seed_genres='
        # for genre in genres:
        #     query_string += genre
        #     query_string += ','
        # query_string = query_string[:-1]

        url = self.url_base + query_string
        r = requests.get(url, verify=True, headers=self.headers)
        if r.status_code // 100 == 2:
            recommended_tracks = self._handle_response(r)
            return recommended_tracks
        else:
            print("Recommendations Request Status Code: " + str(r.status_code))
            exit()

    def _handle_response(self, r):
        """
        Handles recommendations response so we can more easily deal with just tracks
        """
        r = json.loads(r.text)
        tracks = r['tracks']    # there is another key in tracks called 'seeds', figuring this out may be key to better recs
        return tracks

    def get_ordered_genres(self, artists):
        """
        Gets ordered list of genres based on how many of your top artists are in each genre
        """
        top_genres = {}
        for artist in artists:
            genres = artist['genres']
            for genre in genres:
                if genre in top_genres:
                    top_genres[genre] += 1
                else:
                    top_genres[genre] = 1
        return top_genres

    def get_rec_cookie_data(self, tops, time_range):
        """
        Gets top 5 artists, tracks, and genres
        """
        top_tracks = tops['tracks'][time_range]
        top_artists = tops['artists'][time_range]

        top_genres = self.get_ordered_genres(tops['artists'][time_range])
        sorted_genres = sorted(top_genres.items(), key=operator.itemgetter(1))[::-1]
        top_genres = [genre[0] for genre in sorted_genres][0:5]

        top_track_ids = [track['spotify_id'] for track in top_tracks][0:5]
        top_artist_ids = [artist['spotify_id'] for artist in top_artists][0:5]
        return {'track_ids': top_track_ids, 'artist_ids': top_artist_ids, 'genres': top_genres}
