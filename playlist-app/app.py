from turtle import title
from flask import Flask, redirect, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Playlist, Song, PlaylistSong
from forms import NewSongForPlaylistForm, SongForm, PlaylistForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///playlist-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = "vansusopen"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def root():
    """Homepage: redirect to /playlists."""

    return redirect("/playlists")


##############################################################################
# Playlist routes


@app.route("/playlists")
def show_all_playlists():
    """Return a list of playlists."""

    playlists = Playlist.query.all()
    return render_template("playlists.html", playlists=playlists)


@app.route("/playlists/<int:playlist_id>")
def show_playlist(playlist_id):
    """Show detail on specific playlist."""

    # Get the playlist object in the database
    playlist = Playlist.query.get_or_404(playlist_id)
    # Get songs in playlist
    songs = [Song.query.get_or_404(s.id) for s in playlist.songs]
    # songs = Song.query.join(PlaylistSong).filter(Song.id == PlaylistSong.song_id).join(
    #     Playlist).filter(PlaylistSong.playlist_id == Playlist.id).all()

    return render_template('playlist.html', playlist=playlist, songs=songs)


@app.route("/playlists/add", methods=["GET", "POST"])
def add_playlist():
    """Handle add-playlist form:

    - if form not filled out or invalid: show form
    - if valid: add playlist to SQLA and redirect to list-of-playlists
    """
    form = PlaylistForm()

    if form.validate_on_submit():

        # Get form data and create playlist object
        name = form.name.data
        description = form.description.data or None

        playlist = Playlist(
            name=name,
            description=description,
        )

        # Send the new playlist to the database
        db.session.add(playlist)
        db.session.commit()

        return redirect("/playlists")

    return render_template('new_playlist.html', form=form)


##############################################################################
# Song routes


@app.route("/songs")
def show_all_songs():
    """Show list of songs."""

    songs = Song.query.all()
    return render_template("songs.html", songs=songs)


@app.route("/songs/<int:song_id>")
def show_song(song_id):
    """return a specific song"""

    # Get the song object in the database
    song = Song.query.get_or_404(song_id)

    # Get Playlist having song
    # using relationship
    playlists = [Playlist.query.get_or_404(p.id) for p in song.playlists]

    # or using queries
    # playlists = Playlist.query.join(PlaylistSong).filter(Playlist.id == PlaylistSong.playlist_id).join(
    #     Song).filter(PlaylistSong.song_id == Song.id).all()

    return render_template('song.html', song=song, playlists=playlists)


@app.route("/songs/add", methods=["GET", "POST"])
def add_song():
    """Handle add-song form:

    - if form not filled out or invalid: show form
    - if valid: add playlist to SQLA and redirect to list-of-songs
    """

    form = SongForm()

    if form.validate_on_submit():

        # Get form data and create song object
        title = form.title.data
        artist = form.artist.data or None

        song = Song(
            title=title,
            artist=artist
        )

        # Send the new song to the database
        db.session.add(song)
        db.session.commit()

        return redirect("/songs")

    return render_template('new_song.html', form=form)


@app.route("/playlists/<int:playlist_id>/add-song", methods=["GET", "POST"])
def add_song_to_playlist(playlist_id):
    """Add a playlist and redirect to list."""

    playlist = Playlist.query.get_or_404(playlist_id)
    form = NewSongForPlaylistForm()

    # Restrict form to songs not already on this playlist

    curr_on_playlist = [s.id for s in playlist.songs]
    # Populate the choice of songs available for the playlist
    form.song.choices = (db.session.query(Song.id, Song.title)
                         .filter(Song.id.notin_(curr_on_playlist))
                         .all())

    if form.validate_on_submit():

        # This is one way you could do this ...
        playlist_song = PlaylistSong(song_id=form.song.data,
                                     playlist_id=playlist_id)
        db.session.add(playlist_song)
        db.session.commit()

        return redirect(f"/playlists/{playlist_id}")

    return render_template("add_song_to_playlist.html",
                           playlist=playlist,
                           form=form)
