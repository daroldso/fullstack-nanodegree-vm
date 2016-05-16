from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Genre, Base, Artist, User
import datetime

from flask import session as login_session
import string, random

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Duration of artist considered to be 'New'
NEW_ARTIST_EXPIRY_DURATION = 30
# Client ID from client_secrets.json
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Check if csrf token match with the one in login session
    if request.args.get('csrf_token') != login_session['csrf_token']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get code
    code = request.data

    try:
        # Upgrade the code into a credentials object with oauthclient flow
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Sending the access token to Google to check if the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Check if the returned gplus id match with credentials gplus id
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the returned issued_to id match with client id in client secrets
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the user is already logged in by checking if credentials already stored
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If everything okay, store the credentials to login session
    login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # use the credential access token to request logged in user info from Google
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # Store the user info to login session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user already registered. Create one if doesn't
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Return results
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    # Check if credentials exist in login session
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Log user out
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # Return result
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Check if csrf token match with the one in login session
    if request.args.get('csrf_token') != login_session['csrf_token']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get code
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    token = result.split("&")[0]
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s"% url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home'))

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/login')
def showLogin():
    csrf_token = ''.join(random.choice(string.ascii_letters + string.digits) for x in xrange(32))
    login_session['csrf_token'] = csrf_token
    return render_template('login.html', csrf_token=csrf_token)

def login_required(f):
    @wraps(f)
    def is_user_logged_in(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return is_user_logged_in

@app.route('/')
def home():
    genres = session.query(Genre).all()
    # Get the time difference with today and expiry duration we defined earlier
    currentTime = datetime.datetime.today()
    timeDifference = currentTime - datetime.timedelta(days=NEW_ARTIST_EXPIRY_DURATION)
    # Fetch the artists created within expiry duration
    artists = session.query(Artist).filter(
        Artist.created_at > timeDifference).order_by(desc(Artist.created_at))

    for artist in artists:
        print artist.created_at

    return render_template('home.html', genres=genres, artists=artists)

@app.route('/genres/<int:genre_id>/')
def showGenreArtists(genre_id):
    genres = session.query(Genre).all()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    return render_template('showGenreArtist.html', genres=genres, genre=genre)

@app.route('/artists/new', methods=['GET', 'POST'])
@login_required
def newArtist():
    genres = session.query(Genre).all()
    if request.method == 'POST':
        newArtist = Artist(name=request.form['artistName'], biography=request.form['artistBio'], created_at=datetime.datetime.today(), genre_id=request.form['artistGenre'], user_id=login_session['user_id'])
        session.add(newArtist)
        session.commit()
        flash('New Artist %s Successfully Created' % (newArtist.name))
        return redirect(url_for('home'))
    else:
        return render_template('newArtist.html', genres=genres)

@app.route('/artists/<int:artist_id>/')
def showArtist(artist_id):
    genres = session.query(Genre).all()
    try:
        # In case user put in a random number into the url
        artist = session.query(Artist).filter_by(id=artist_id).one()
    except:
        return redirect(url_for('home'))
    biography = artist.biography.encode().split('\n')
    return render_template('showArtist.html', genres=genres, artist=artist, biography=biography)

def is_user_authed(uid, sess_id):
    """Tests whether a user is authorized to make CRUD action"""
    if uid != sess_id:
        abort(403)
    else:
        return True

@app.route('/artists/<int:artist_id>/edit/', methods=['GET', 'POST'])
@login_required
def editArtist(artist_id):
    genres = session.query(Genre).all()
    try:
        editedArtist = session.query(Artist).filter_by(id=artist_id).one()
    except:
        return redirect(url_for('home'))
    if is_user_authed(editedArtist.user_id, login_session['user_id']) and request.method == 'POST':
        if request.form['artistName']:
            editedArtist.name =request.form['artistName']
        if request.form['artistBio']:
            editedArtist.biography =request.form['artistBio']
        if request.form['artistGenre']:
            editedArtist.genre_id =request.form['artistGenre']
        session.add(editedArtist)
        session.commit()
        flash('Artist Successfully Edited')
        return redirect(url_for('home'))
    else:
        return render_template('editArtist.html', artist=editedArtist, genres=genres)

@app.route('/artists/<int:artist_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteArtist(artist_id):
    try:
        deletedArtist = session.query(Artist).filter_by(id=artist_id).one()
    except:
        return redirect(url_for('home'))
    if is_user_authed(deletedArtist.user_id, login_session['user_id']) and request.method == 'POST':
        session.delete(deletedArtist)
        session.commit()
        flash('Artist Successfully Deleted')
        return redirect(url_for('home'))
    else:
        return render_template('deleteArtist.html', artist=deletedArtist)

@app.route('/genres.json')
def genresJSON():
    genres = session.query(Genre).all()
    items = []
    for genre in genres:
        serialized = {
            'name': genre.name,
            'id': genre.id,
            'artists': []
        }
        for artist in genre.artists:
            serialized['artists'].append({
                'id': artist.id,
                'name': artist.name,
                'biography': artist.biography,
                'genre_id': artist.genre.id,
                'created_at': str(artist.created_at),
                })
        items.append(serialized)
    return jsonify(genres=items)

@app.route('/artists.json')
def artistsJSON():
    artists = session.query(Artist).all()
    return jsonify(artists=[i.serialize for i in artists])

@app.route('/artists/<int:artist_id>/json')
def artistJSON(artist_id):
    artist = session.query(Artist).filter_by(id=artist_id).one()
    return jsonify(artist.serialize)

@app.route('/genres/<int:genre_id>/artists.json')
def genreArtistsJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Artist).filter_by(
        genre_id=genre_id).all()
    return jsonify(artists=[i.serialize for i in items])

@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
