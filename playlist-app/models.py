"""Models for Playlist app."""

from codecs import unicode_escape_decode
from enum import unique
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.
    To be call in app file
    """

    db.app = app
    db.init_app(app)


#################################
#Tables and relationships

class Playlist(db.Model):
    """Playlist."""

    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    # playlist to palylistsong and back
    assignment = db.relationship('PlaylistSong', backref='playlists')
    # playlist to song and back using playlistsong
    # songs = db.relationship(
    #     'Song', secondary='playlists_songs', backref='playlists')

    def to_dict(self):
        """Serialize playlist to a dictionary of info."""

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class Song(db.Model):
    """Song."""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)

    # song to playlistsong and back
    assignment = db.relationship('PlaylistSong', backref='songs')
    # song to playlist and back using playlistsong
    # playlists = db.relationship(
    #     'Playlist', secondary='playlists_songs', backref='songs')

    def to_dict(self):
        """Serialize song to a dictionary of info."""

        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
        }


class PlaylistSong(db.Model):
    """Mapping of a playlist to a song."""

    __tablename__ = "playlists_songs"

    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer,  db.ForeignKey(
        'playlists.id'), nullable=False, unique=True)
    song_id = db.Column(db.Integer, db.ForeignKey(
        'songs.id'), nullable=False, unique=True, )
