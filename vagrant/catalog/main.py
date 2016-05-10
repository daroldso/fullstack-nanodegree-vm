from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Genre, Base, Artist, User
from flask import session as login_session
import datetime

app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Duration of artist considered to be 'New'
NEW_ARTIST_EXPIRY_DURATION = 30

@app.route('/')
def home():
    genres = session.query(Genre).all()
    # Get the time difference with today and expiry duration we defined earlier
    currentTime = datetime.datetime.today()
    timeDifference = currentTime - datetime.timedelta(days=NEW_ARTIST_EXPIRY_DURATION)
    # Fetch the artists created within expiry duration
    artists = session.query(Artist).filter(
        Artist.created_at > timeDifference).order_by(desc(Artist.created_at))

    return render_template('home.html', genres=genres, artists=artists)

@app.route('/artists/new', methods=['GET', 'POST'])
def newArtist():
    return render_template('newArtist.html')

@app.route('/artists/<int:artist_id>/', methods=['GET', 'POST'])
def showArtist(artist_id):
    artist = session.query(Artist).filter_by(id=artist_id).one()
    biography = artist.biography.encode().split('\n')
    return render_template('showArtist.html', artist=artist, biography=biography)

@app.route('/artists/edit', methods=['GET', 'POST'])
def editArtist():
    return render_template('editArtist.html')

@app.route('/artists/delete', methods=['GET', 'POST'])
def deleteArtist():
    return render_template('deleteArtist.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
