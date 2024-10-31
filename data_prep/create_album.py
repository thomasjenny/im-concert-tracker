from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import json
import os


def create_albums_table(albums_json):

    albums = pd.json_normalize(albums_json)

    albums_exploded = albums.explode("media", ignore_index=True)
    media_normalized = pd.json_normalize(albums_exploded["media"], sep="_")
    media_normalized.columns = [f"media_{col}" for col in media_normalized.columns]
    albums_exploded = albums_exploded.join(media_normalized)

    albums_final = albums_exploded[["title", "media_recording_title"]].rename(
        columns={"title": "album_title", "media_recording_title": "song_title"}
    )
    return albums_final


if __name__ == "__main__":
    # Load raw JSON data
    in_path = Path.cwd() / "data_prep" / "data" / "json_raw"
    in_songs_file = "musicbrainz_songs.json"

    with open(Path(in_path / in_songs_file), "r") as songs_file:
        albums = json.load(songs_file)

    albums = create_albums_table(albums)
    print(albums)

    out_path = Path.cwd() / "data_prep" / "data" / "out_test"
    albums.to_csv(Path(out_path / "albums_normalize_test.csv"))
