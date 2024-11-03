import json
import os
from pathlib import Path
from typing import Dict

import pandas as pd

from clean_album_data import clean_album_data
from clean_setlists_data import clean_setlists_data
import data_prep
from join_setlists_albums import join_setlists_albums
import musicbrainz
import setlist_fm


def run_data_pipeline(
    mbid: str,
    headers: Dict[str, str],
    missing_tour_data: pd.DataFrame,
    call_api: bool = True,
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
        songs = musicbrainz.get_songs(releases, test=False)
    else:
        in_path = Path(Path.cwd() / "data_prep" / "data" / "json_raw")
        in_setlists_file = "setlist_fm_setlists.json"
        in_songs_file = "musicbrainz_songs.json"

        with open(Path(in_path / in_setlists_file), "r") as setlists_file:
            setlists = json.load(setlists_file)
        with open(Path(in_path / in_songs_file), "r") as songs_file:
            songs = json.load(songs_file)

    # Initial data cleaning and normalization
    setlists = clean_setlists_data(setlists, missing_tour_data)
    albums = clean_album_data(songs)
    concerts = join_setlists_albums(setlists, albums)

    # Prepare data for app
    app_setlists = data_prep.prepare_setlists(concerts)
    app_concerts_per_city = data_prep.prepare_concerts_per_city(concerts)
    app_albums_total = data_prep.prepare_albums_total(concerts)

    return app_setlists, app_concerts_per_city, app_albums_total


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

    # in_path =

    missing_tour_data_file = Path.cwd() / "data_prep" / "data" / "missing_tour_data.csv"
    missing_tour_data = pd.read_csv(missing_tour_data_file)

    a, b, c = run_data_pipeline(mbid, headers, missing_tour_data, call_api=False)

    print(a.head())
    print(b.head())
    print(c.head())