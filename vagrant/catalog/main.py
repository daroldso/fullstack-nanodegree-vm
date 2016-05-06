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

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
