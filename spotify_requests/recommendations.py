import json
import requests
import operator

class Recommendations:
    def __init__(self, header):
        self.url_base = 'https://api.spotify.com/v1/recommendations'
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}

    def get_recommendations(self, stats, track_ids=[], artist_ids=[], genres=[]):
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
        query_string += '&target_danceability='+ str(stats['ave_danceability'])
        query_string += '&target_valence='+ str(stats['ave_valence'])
        query_string += '&target_energy='+ str(stats['ave_energy'])
        query_string += '&target_speechiness='+ str(stats['ave_speechiness'])
        query_string += '&target_duration='+ str(int(stats['ave_duration']) * 1000)
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
        print("Recommendations Request Status Code: " + str(r.status_code))
        if r.status_code // 100 == 2:
            recommended_tracks = self._handle_response(r)
            return recommended_tracks
        else:
            return False

    def _handle_response(self, r):
        """
        Handles recommendations response so we can more easily deal with just tracks
        """
        r = json.loads(r.text)
        tracks = r['tracks']    # there is another key in tracks called 'seeds', figuring this out may be key to better recs
        return tracks

    def get_genre_frequency(self, artists):
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

    def get_rec_cookie_data(self, tops, time_range, auth_header):
        """
        Gets top 5 artists, tracks, and genres
        """
        top_tracks = tops['tracks'][time_range]
        top_artists = tops['artists'][time_range]
        tg = TrackGrabber(auth_header)
        stats = tg.get_stats(top_tracks)

        top_genres = self.get_genre_frequency(tops['artists'][time_range])   # sort genres list
        sorted_genres = sorted(top_genres.items(), key=operator.itemgetter(1))[::-1]

        if len(top_genres) >= 5:
            top_genres = [genre[0] for genre in sorted_genres][0:5]
        else:
            top_genres = [genre[0] for genre in sorted_genres]
        if len(top_tracks) >= 5:
            top_track_ids = [track['spotify_id'] for track in top_tracks][0:5]
        else:
            top_track_ids = [track['spotify_id'] for track in top_tracks]
        if len(top_artists) >= 5:
            top_artist_ids = [artist['spotify_id'] for artist in top_artists][0:5]
        else:
            top_artist_ids = [artist['spotify_id'] for artist in top_artists]

        return {'track_ids': top_track_ids, 'artist_ids': top_artist_ids, 'genres': top_genres, 'stats': stats}
