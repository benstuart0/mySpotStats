from urllib.parse import quote
from flask import Flask, render_template, redirect, json, session, request
from spotify_requests import spotify
from spotify_requests.track import TrackGrabber
from spotify_requests.artist import ArtistGrabber
from spotify_requests.user import UserGrabber
import sys
import aws.dynamo as dynamo

app = Flask(__name__)
app.secret_key = 'thisIsTheSecretKeyAYYYY'
app.config['SESSION_TYPE'] = 'filesystem'

times = {
    'short_term': 'Last Month',
    'medium_term': 'Last 6 Months',
    'long_term': 'All Time'
}

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"

CLIENT = json.load(open('conf.json', 'r+'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']

SCOPE = "user-read-private user-top-read playlist-modify-private user-read-email"
REDIRECT_URI = CLIENT['redirect_uri']
#REDIRECT_URI = 'http://myspotstats.herokuapp.com/callback' # uncomment for production

@app.route('/')
def home():
    if 'auth_header' in session:
        # place user data in dynamoDB for (hopefully) later use
        ug = UserGrabber(session['auth_header'])
        user = ug.get_user()
        dynamo.update_db(user, session['auth_header'])

        type = request.args.get('type')
        time_range = request.args.get('time_range')
        if type and time_range:
            return redirect('/tracks/'+time_range) if type=='tracks' else redirect('/artists/'+time_range)
        elif type:
            return redirect('/tracks') if type=='tracks' else redirect('/artists')

        return render_template('home.html')
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
    auth_header = spotify.authorize(auth_token, REDIRECT_URI)
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
