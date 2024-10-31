from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import json
import os


def clean_data():


    setlists = pd.json_normalize(setlists)
    setlists = setlists[
        [
            "id",
            "eventDate",
            "venue.id",
            "venue.name",
            "venue.city.id",
            "venue.city.name",
            "venue.city.stateCode",
            "venue.city.coords.lat",
            "venue.city.coords.long",
            "venue.city.country.name",
            "tour.name",
            "sets.set",
        ]
    ]

    # Step 1: Explode the 'details' column so each row represents an item in the list
    setlists_exploded = setlists.explode("sets.set", ignore_index=True)
    # Step 2: Normalize the 'details' column to flatten nested dictionaries
    setlists_normalized = pd.json_normalize(setlists_exploded["sets.set"])
    # Step 3: Drop the now-redundant 'details' column from df_exploded
    setlists_exploded = setlists_exploded.drop(columns=["sets.set"])
    # Step 4: Combine the exploded DataFrame with the normalized details DataFrame
    setlists_combined = setlists_exploded.join(setlists_normalized)
    # Step 5: Further explode the 'song' column to handle the list of song dictionaries
    setlists_combined = setlists_combined.explode("song", ignore_index=True)
    # Step 6: Normalize the 'song' column to separate song details into individual columns
    song_normalized = pd.json_normalize(setlists_combined["song"]).rename(
        columns={"name": "name_new", "tape": "tape_new"}
    )
    # Step 7: Drop the now-redundant 'song' column and join with song details
    setlists_combined = setlists_combined.drop(columns=["song"]).join(song_normalized)

    print(setlists_combined.columns.tolist())

    setlists = setlists_combined.drop(
        [
            "name",
            "cover.mbid",
            "cover.sortName",
            "cover.disambiguation",
            "cover.url",
            "info",
            "with.mbid",
            "with.name",
            "with.sortName",
            "with.disambiguation",
            "with.url",
        ],
        axis=1,
    )


if __name__ == "__main__":
    # Load raw JSON data
    in_path = Path.cwd() / "data_prep" / "data" / "json_raw"
    in_setlists_file = "setlist_fm_setlists.json"
    in_songs_file = "musicbrainz_songs.json"

    with open(Path(in_path / in_setlists_file), "r") as setlists_file:
        setlists = json.load(setlists_file)
    with open(Path(in_path / in_songs_file), "r") as songs_file:
        albums = json.load(songs_file)


    out_path = Path.cwd() / "data_prep" / "data" / "out_test"
    setlists.to_csv(Path(out_path / "json_normalize_test.csv"))
