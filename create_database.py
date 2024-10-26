import json
import os
from pathlib import Path
from typing import Dict

from sqlalchemy import create_engine, Integer, Boolean

import create_tables
import data_cleaning
import musicbrainz
import setlist_fm


def create_database(
    mbid: str, headers: Dict[str, str], call_api: Boolean = True
) -> None:
    """Create an SQLite db for the concert, venue, city, setlist, and
    album tables.

    Args:
        mbid (str): MBID of the artist for which the data should be
            queried
        headers (dict): API headers for the setlist.fm API
        call_api (bool): determines the source of the data. If set to 
            True, the data is obtained via API calls. If set to False,
            local data is used instead (e.g., for testing).
    
    Returns:
        None
    """
    if call_api == True:
        # Query setlists from setlist.fm
        setlists = setlist_fm.get_setlists(mbid, headers)
        # Query releases for artist MBID from Musicbrainz
        releases = musicbrainz.get_releases(mbid)
        # Query songs for each release
        songs = musicbrainz.get_songs(releases, test = False)
    else:
        in_path = Path.cwd() / "data" / "json_raw"
        in_setlists_file = "setlist_fm_setlists.json"
        in_songs_file = "musicbrainz_songs.json"

        with open(Path(in_path / in_setlists_file), "r") as setlists_file:
            setlists = json.load(setlists_file)
        with open(Path(in_path / in_songs_file), "r") as songs_file:
            songs = json.load(songs_file)

    # Create dataframes for database tables
    concert, venue, city = create_tables.create_concert_venue_city_tables(setlists)
    setlist = create_tables.create_setlist_table(setlists)
    album = create_tables.create_albums_table(songs)

    # Data cleaning
    album = data_cleaning.clean_album_table(album)
    setlist = data_cleaning.clean_setlist_table(setlist)
    data_completion_file = Path(Path.cwd() / "data" / "tour_info_completion.csv")
    concert = data_cleaning.add_missing_tours(concert, data_completion_file)

    # Insert into SQLite database
    db_out_path = Path.cwd() / "data" / "db"
    os.makedirs(db_out_path, exist_ok=True)
    db_out_name = "iron_maiden_concerts.db"

    city_id_dtype = {"city_id": Integer}
    setlist_pos_dtype = {"setlist_position": Integer}

    engine = create_engine(f"sqlite:///{db_out_path}/{db_out_name}", echo=True)
    with engine.begin() as conn:
        concert.to_sql(
            "concert", conn, if_exists="replace", index=False, dtype=city_id_dtype
        )
        venue.to_sql(
            "venue", conn, if_exists="replace", index=False, dtype=city_id_dtype
        )
        city.to_sql("city", conn, if_exists="replace", index=False, dtype=city_id_dtype)
        setlist.to_sql(
            "setlist", conn, if_exists="replace", index=False, dtype=setlist_pos_dtype
        )
        album.to_sql("album", conn, if_exists="replace", index=False)
    
    print(f"{db_out_name} successfully created!")
    
    return None

if __name__ == "__main__":
    from dotenv import load_dotenv

    mbid = "ca891d65-d9b0-4258-89f7-e6ba29d83767"

    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    headers = {
        "x-api-key": API_KEY,
        "Accept": "application/json",
        "Accept-Languate": "en",
    }

    create_database(mbid, headers, call_api = True)
