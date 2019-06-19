from urllib.parse import quote
from flask import Flask, render_template, redirect, json, session, request
from spotify_requests import spotify
from spotify_requests.track import TrackGrabber
from spotify_requests.artist import ArtistGrabber
import sys

app = Flask(__name__)
app.secret_key = 'thisIsTheSecretKeyAYYYY'
app.config['SESSION_TYPE'] = 'filesystem'

times = {
    'short_term': '3 Weeks',
    'medium_term': '6 Months',
    'long_term': 'All Time'
}

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"

CLIENT = json.load(open('conf.json', 'r+'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']
REDIRECT_URI = CLIENT['redirect_uri']

SCOPE = "user-read-private user-top-read"


@app.route('/')
def home():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        tg = TrackGrabber(auth_header)
        tracks = tg.main('long_term',50,0)
        stats = tg.get_stats(tracks)
        time_range = tg.time_range
        return render_template('tracks.html', tracks=tracks, stats=stats, time=times[time_range])
    return auth()

@app.route('/tracks')
@app.route('/tracks/<time_range>')
def tracks(time_range="long_term"):
    if 'auth_header' in session:
        auth_header = session['auth_header']
        tg = TrackGrabber(auth_header)
        tracks = tg.main(time_range,49,0) + tg.main(time_range,50,49)
        stats = tg.get_stats(tracks)
        return render_template('tracks.html', tracks=tracks, stats=stats, time=times[time_range])
    return auth()

@app.route('/artists')
@app.route('/artists/<time_range>')
def artists(time_range="long_term"):
    if 'auth_header' in session:
        auth_header = session['auth_header']
        ag = ArtistGrabber(auth_header)
        artists = ag.main(time_range,49,0) + ag.main(time_range,50,49)  # gets top 99 artists (can only query 50 at a time)
        popularity = ag.get_pop_rating(artists)
        return render_template('artists.html', artists=artists, popularity=popularity, time=times[time_range])
    return auth()

@app.route('/callback')
def callback():
    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header
    return home()

@app.route('/auth')
def auth():
    return redirect(SPOTIFY_AUTH_URL+ '?response_type=code'
    + '&client_id=' + CLIENT_ID
    + '&scope=' + quote(SCOPE.encode("utf-8")) +
    '&redirect_uri=' +  quote(REDIRECT_URI.encode("utf-8")))

if __name__ == "__main__":
    session.init_app(app)
    app.debug = True
    app.run()
