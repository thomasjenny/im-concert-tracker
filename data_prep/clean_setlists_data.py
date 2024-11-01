from typing import List, Dict

import numpy as np
import pandas as pd


def clean_setlists_data(
    raw_setlists_data: List[Dict], tour_data_completion_df: pd.DataFrame
) -> pd.DataFrame:
    """Normalize the setlist.fm setlists data and perform some data
    cleaning operations: normalize the JSON structure, harmonize song
    names, drop data that is not required.

    Args:
        raw_setlists_data (list): the raw setlist.fm setlists data in
            JSON format
        tour_data_completion_df (pd.DataFrame): DataFrame containing
            the tour names for records where they are missing
    
    Returns:
        setlists (pd.DataFrame): DataFrame containing the cleaned and
            harmonized data
    """
    setlists = pd.json_normalize(raw_setlists_data)
    setlists = setlists[
        [
            "id",
            "eventDate",
            "venue.name",
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

    setlists = setlists_combined.drop(
        columns=[
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
    )

    # Replace song names
    replacement_mapping_dict = {
        "633 Squadron": '"633 Squadron" Theme',
        "633 Squadron Theme": '"633 Squadron" Theme',
        'Intro - "633 Squadron" theme': '"633 Squadron" Theme',
        "Intro - 633 Squadron music": '"633 Squadron" Theme',
        'Theme from "633 Squadron"': '"633 Squadron" Theme',
        "Always Look on the Bright Side": "Always Look on the Bright Side of Life",
        "Blade Runner": "Blade Runner (End Titles)",
        "Blade Runner (end titles)": "Blade Runner (End Titles)",
        "Blade Runner Intro": "Blade Runner (End Titles)",
        "Blade Runner Soundtrack": "Blade Runner (End Titles)",
        "Bladerunner Theme": "Blade Runner (End Titles)",
        "Churchill Speech": "Churchill's Speech",
        "Churchill’s Speech": "Churchill's Speech",
        "Intro - Churchill's Speech": "Churchill's Speech",
        "Intro: Churchill's Speech": "Churchill's Speech",
        'Intro - Main Title from the movie "Where Eagles Dare"': '"Main Title" from "Where Eagles Dare"',
        "Where Eagles Dare Main Theme": '"Main Title" from "Where Eagles Dare"',
        "Where Eagles Dare Theme": '"Main Title" from "Where Eagles Dare"',
        "Mars, The Bringer of War": "Mars, the Bringer of War",
    }
    setlists.replace(replacement_mapping_dict, inplace=True)

    # Complete missing tour information
    setlists = setlists.merge(
        tour_data_completion_df,
        left_on="id",
        right_on="concert_id",
        how="left",
        suffixes=("", "_completion"),
    )

    setlists["tour.name"] = setlists["tour.name"].combine_first(setlists["tour"])

    setlists = setlists.drop(
        columns=["concert_id", "venue_id", "city_id", "date", "tour"]
    )

    # Add song count numbers
    setlists["song_count"] = setlists.groupby("id").cumcount() + 1

    # Concatenate city and state
    setlists["venue.city.name"] = np.where(
        setlists["venue.city.country.name"] == "United States",
        setlists["venue.city.name"] + ", " + setlists["venue.city.stateCode"],
        setlists["venue.city.name"],
    )

    setlists = setlists.drop(columns=["venue.city.stateCode"])

    # Rename columns
    setlists = setlists.rename(
        columns={
            "eventDate": "date",
            "venue.name": "venue",
            "venue.city.name": "city",
            "venue.city.coords.lat": "latitude",
            "venue.city.coords.long": "longitude",
            "venue.city.country.name": "country",
            "tour.name": "tour",
            "encore,name_new": "encore",
            "tape_new": "from_tape",
            "name_new": "song_title",
            "cover.name": "cover",
        }
    )

    # Change column order
    new_column_order = [
        "id",
        "date",
        "venue",
        "city",
        "country",
        "latitude",
        "longitude",
        "tour",
        "song_count",
        "song_title",
        "encore",
        "from_tape",
        "cover",
    ]

    setlists = setlists[new_column_order]

    return setlists


if __name__ == "__main__":
    import json
    import os
    from pathlib import Path

    in_path = Path(Path.cwd() / "data_prep" / "data")

    # Load raw JSON data
    in_setlists_file = "setlist_fm_setlists.json"
    with open(Path(in_path / "json_raw" / in_setlists_file), "r") as setlists_file:
        setlists = json.load(setlists_file)

    # Load the missing tour names
    missing_tour_data_file = "missing_tour_data.csv"
    missing_tour_data = pd.read_csv(Path(in_path / missing_tour_data_file))

    # Run the data cleaning function
    setlists = clean_setlists_data(setlists, missing_tour_data)

    # Save the clean data to CSV
    out_path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    os.makedirs(out_path, exist_ok=True)
    setlists.to_csv(Path(out_path / "setlists_clean.csv"), index=False)
