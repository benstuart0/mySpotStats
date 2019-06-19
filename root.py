from urllib.parse import quote
from flask import Flask, render_template, redirect, json, session, request
from spotify_requests import spotify
from track import TrackGrabber
import sys

try:
    import urllib.request, urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibparse

app = Flask(__name__)
app.secret_key = 'thisIsTheSecretKeyAYYYY'
app.config['SESSION_TYPE'] = 'filesystem'

#TOKEN = 'BQDzpL4WSkuEcYXWUF5sU1vTUZYvpG5waH-z3HuKSPwc9HisoJyQ7xIcKYDZtNLw7bHe9TEkT2wtOV34q2jBxn-5MR74NxhRASNc5gChid4Up5H32nHj6A1symK6xRnpeu2QyZbDqmL-KM1N4FKZ-VC4gGKsvGWBFLOHaxp45eispFqCgMNUHI5taGFbEK9fMNg-jBqgCJdbX91uTTuE3pwHegQB'
times = {
    'short_term': '3 Weeks',
    'medium_term': '6 Months',
    'long_term': 'All Time'
}

SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')

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
    return redirect('/auth')

@app.route('/callback')
def callback():
    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header
    return redirect('/')

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
