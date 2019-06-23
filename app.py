import sys
from urllib.parse import quote
from flask import Flask, render_template, redirect, json, session, request, make_response
from spotify_requests import spotify
from spotify_requests.track import TrackGrabber
from spotify_requests.artist import ArtistGrabber
from spotify_requests.user import UserGrabber
from spotify_requests.playlist_creator import PlaylistCreator
import aws.dynamo as dynamo

app = Flask(__name__)
app.secret_key = 'thisIsTheSecretKeyAYYYY'
app.config['SESSION_TYPE'] = 'filesystem'

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
#REDIRECT_URI = 'http://myspotstats.herokuapp.com/callback' # uncomment for production

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

        # place user data in dynamoDB for (hopefully) later use
        data_cookie = request.cookies.get('data_retrieved')
        resp = make_response(render_template('home.html'))
        if not data_cookie or data_cookie != 'yes':
            ug = UserGrabber(session['auth_header'])
            user = ug.get_user()
            dynamo.update_db(user, session['auth_header'])
            resp.set_cookie('data_retrieved', 'yes')
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
        playlist_cancel = request.args.get('playlist_cancel')
        if create_playlist == "Create Playlist":
            if playlist_cancel == 'True':
                print("Hey you canceled the playlist")
                return redirect('/tracks/' + time_range)
            ug = UserGrabber(session['auth_header'])
            user = ug.get_user()
            pc = PlaylistCreator(session['auth_header'], user)
            playlist = pc.create_playlist(times[time_range], tracks)
            if not playlist:
                redirect('/tracks')
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

if __name__ == "__main__":
    session.init_app(app)
    app.debug = True
    app.run()
