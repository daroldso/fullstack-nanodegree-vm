from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return Genre data in JSON format"""
        return {
            'name': self.name,
            'id': self.id,
            'artists': self.artists
        }


class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    biography = Column(String(250))
    created_at = Column(DateTime())
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre, backref='artists')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        '''Return Artist data in JSON format'''
        return {
            'name': self.name,
            'biography': self.biography,
            'created_at': self.created_at,
        }

Genre.posts_query = relationship(Artist, lazy='dynamic')

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)