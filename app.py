import sys
from urllib.parse import quote
from flask import Flask, render_template, redirect, json, session, request, make_response
from spotify_requests import spotify
from spotify_requests.track import TrackGrabber
from spotify_requests.artist import ArtistGrabber
from spotify_requests.user import UserGrabber
from spotify_requests.playlist_creator import PlaylistCreator
from spotify_requests.recommendations import Recommendations
import aws.dynamo as dynamo
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'thisIsTheSecretKeyAYYYY'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TESTING'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

times = {
    'short_term': 'the Last Month',
    'medium_term': 'the Last 6 Months',
    'long_term': 'All Time'
}

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"

CLIENT = json.load(open('conf.json', 'r+'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']

SCOPE = "user-read-private user-top-read playlist-modify-public playlist-modify-private user-read-email playlist-read-private"
REDIRECT_URI = CLIENT['redirect_uri']
# REDIRECT_URI = 'http://myspotstats.herokuapp.com/callback' # uncomment for heroku production
# REDIRECT_URI = 'http://www.myspotstats.com/callback'    # uncomment for live domain

@app.route('/')
def home():
    """
    Home page, redirects to other pages based on user input
    """
    if 'auth_header' in session:
        # get form responses
        type = request.args.get('type')
        time_range = request.args.get('time_range')
        if type and time_range:
            return redirect('/tracks/'+time_range) if type=='tracks' else redirect('/artists/'+time_range)
        elif type:
            return redirect('/tracks') if type=='tracks' else redirect('/artists')

        rec_playlist = request.args.get('create_playlist')
        if rec_playlist == 'rec_playlist':
            return redirect('/recommended4376')

        # place user data in dynamoDB for (hopefully) later use
        data_cookie = request.cookies.get('data_retrieved')
        resp = make_response(render_template('home.html'))
        if not data_cookie or data_cookie != 'yes':
            resp = set_data_cookies(resp)
        try:
            return resp
        except:
            return redirect('/auth')    # send to auth if homepage doesn't load

    return redirect('/auth')

@app.route('/tracks')
@app.route('/tracks/<time_range>')
def tracks(time_range="long_term"):
    """
    Track list pages
    """
    if 'auth_header' in session:
        tg = TrackGrabber(session['auth_header'])
        tracks = tg.main(time_range,49,0) + tg.main(time_range,50,49)
        stats = tg.get_stats(tracks)

        create_playlist = request.args.get('create_playlist')
        if create_playlist == "tops_playlist":
            return tops_playlist(tracks, time_range)

        return render_template('tracks.html', tracks=tracks, stats=stats, time=times[time_range])
    return redirect('/auth')

@app.route('/artists')
@app.route('/artists/<time_range>')
def artists(time_range="long_term"):
    """
    Artist list pages
    """
    if 'auth_header' in session:
        ag = ArtistGrabber(session['auth_header'])
        artists = ag.main(time_range,49,0) + ag.main(time_range,50,49)  # gets top 99 artists (can only query 50 at a time)
        popularity = ag.get_pop_rating(artists)
        return render_template('artists.html', artists=artists, popularity=popularity, time=times[time_range])
    return redirect('/auth')

@app.route('/recommended4376')
def recommend(time_range='medium_term'):
    """
    Endpoint that creates recommended playlist
    """
    top_tracks = json.loads(request.cookies.get('top_tracks'))
    top_artists = json.loads(request.cookies.get('top_artists'))
    top_genres = json.loads(request.cookies.get('top_genres'))
    stats = json.loads(request.cookies.get('track_stats'))
    rec = Recommendations(session['auth_header'])
    recommended_tracks = rec.get_recommendations(stats, top_tracks,top_artists,top_genres)

    if not recommended_tracks:  # error handling
        return render_template('playlist_failed.html')

    ug = UserGrabber(session['auth_header'])
    user = ug.get_user()
    pc = PlaylistCreator(session['auth_header'], user)
    playlist_name = "Recommended by mySpotStats"
    playlist_description = "Songs recommended by mySpotStats algorithm."
    rec_playlist = pc.create_playlist(times[time_range], recommended_tracks, playlist_name, playlist_description)
    return render_template('playlist_created.html')

@app.route('/callback')
def callback():
    """
    Called from Auth endpoint. Retrieves auth token and redirects to home page.
    """
    auth_token = request.args['code']
    session['auth_header'] = spotify.authorize(auth_token, REDIRECT_URI)
    return redirect('/')

@app.route('/auth')
def auth():
    """
    Signs into spotify account
    """
    return redirect(SPOTIFY_AUTH_URL+ '?response_type=code'
    + '&client_id=' + CLIENT_ID
    + '&scope=' + quote(SCOPE.encode("utf-8")) +
    '&redirect_uri=' +  quote(REDIRECT_URI.encode("utf-8")))

def tops_playlist(tracks, time_range='long_term'):
    """
    Method to create playlist of top tracks from tracks page.
    """
    ug = UserGrabber(session['auth_header'])
    user = ug.get_user()

    pc = PlaylistCreator(session['auth_header'], user)
    playlist_name = "My Top Tracks of " + times[time_range]
    playlist_description = "My 99 most listened to tracks of " + times[time_range]
    playlist = pc.create_playlist(times[time_range], tracks, playlist_name, playlist_description)

    if not playlist:    # error handling
        return render_template('playlist_failed.html')

    return render_template('playlist_created.html')

def set_data_cookies(resp):
    """
    Method to set essential cookies to hold basic user data
    """
    tomorrow = datetime.now() + timedelta(days=1)
    ug = UserGrabber(session['auth_header'])    # updates database with user data
    user = ug.get_user()
    user_tops = dynamo.update_db(user, session['auth_header'])
    resp.set_cookie('data_retrieved', 'yes', expires=tomorrow)

    # cache user tops for recommendations
    rec = Recommendations(session['auth_header'])
    rec_cookie_data = rec.get_rec_cookie_data(user_tops, 'short_term', session['auth_header'])
    resp.set_cookie('top_tracks', json.dumps(rec_cookie_data['track_ids']), expires=tomorrow)
    resp.set_cookie('top_artists', json.dumps(rec_cookie_data['artist_ids']), expires=tomorrow)
    resp.set_cookie('top_genres', json.dumps(rec_cookie_data['genres']), expires=tomorrow)
    stats = convert_stats(rec_cookie_data['stats'])
    resp.set_cookie('track_stats', json.dumps(stats), expires=tomorrow)
    return resp

def convert_stats(stats):
    return {
        'ave_danceability': float(stats['ave_danceability']),
        'ave_valence': float(stats['ave_valence']),
        'ave_energy': float(stats['ave_energy']),
        'ave_speechiness': float(stats['ave_speechiness']),
        'ave_duration': float(stats['ave_duration']),
    }

@app.errorhandler(401)
def handle_401():
    return redirect('/auth')

if __name__ == "__main__":
    session.init_app(app)
    app.debug = True
    app.run()
