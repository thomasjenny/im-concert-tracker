import os
from dotenv import load_dotenv

import setlist_fm
import musicbrainz
import create_tables

# Get setlists
# Headers for setlist.fm API call
load_dotenv()
API_KEY = os.getenv("API_KEY")
headers = {
    "x-api-key": API_KEY,
    "Accept": "application/json",
    "Accept-Languate": "en",
}

mbid = "ca891d65-d9b0-4258-89f7-e6ba29d83767"

setlists = setlist_fm.get_setlists(mbid, headers)

# Get releases
releases = musicbrainz.get_releases(mbid)

# Get songs
songs = musicbrainz.get_songs(releases)

# Create tables
# Convert, venue, city
concert, venue, city = create_tables.create_concert_venue_city_tables(setlists)

# Setlists
setlist = create_tables.create_setlist_table(setlists)

# Albums
album = create_tables.create_albums_table(songs)


# TODO: data cleaning
# TODO: export to SQLite
