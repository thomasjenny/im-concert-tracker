from typing import List, Dict

import pandas as pd


def clean_album_data(releases: List[Dict]) -> pd.DataFrame:
    """Normalize the musicbrainz albums/songs data and ....

    Args:
        releases (list): list of all releases fetched from the API

    Returns:
        albums (dataframe): albums table in pandas dataframe format
    """
    column_names = [
        "album_name",
        "song_position",
        "song_name",
    ]

    columns = {col_name: [] for col_name in column_names}

    for release in releases:
        # Media contains the track information
        for media in release.get("media"):
            # tracks is a list of dicts containing song information
            for track in media.get("tracks"):
                # Album name is in the top-level dict
                columns["album_name"].append(release.get("title"))
                columns["song_position"].append(track.get("position"))
                columns["song_name"].append(track.get("title"))

    albums = pd.DataFrame(
        list(
            zip(
                columns["album_name"],
                columns["song_position"],
                columns["song_name"],
            )
        ),
        columns=["album_name", "song_position", "song_name"],
    )

    # Filter on studio albums only
    studio_albums = [
        "Iron Maiden",
        "Killers",
        "The Number Of The Beast",
        "Piece of Mind",
        "Powerslave",
        "Somewhere in Time",
        "Seventh Son of a Seventh Son",
        "No Prayer for the Dying",
        "Fear of the Dark",
        "The X Factor",
        "Virtual XI",
        "Brave New World",
        "Dance of Death",
        "A Matter of Life and Death",
        "The Final Frontier",
        "The Book of Souls",
        "Senjutsu",
    ]

    # Filter studio albums only
    albums = albums[albums["album_name"].isin(studio_albums)].reset_index(drop=True)
    # Drop duplicate song names
    albums = albums.drop_duplicates(subset=["album_name", "song_name"])
    albums = albums.sort_values(by=["album_name", "song_position"]).reset_index(
        drop=True
    )

    # Delete some rows
    to_delete = [
        "making of",
        "video",
        "studio performance",
        "photo",
        "5.1",
        "remaster",
        "live",
        "'88",
    ]

    # Last part is for Japanese
    delete_pattern = "|".join(to_delete) + r"|[\u3040-\u30FF\u4E00-\u9FFF]"

    albums = albums[
        ~albums["song_name"].str.contains(delete_pattern, case=False, na=False)
    ]

    # Replace song names in the album df with the way they are written in
    # the setlists df
    song_name_harmonization = {
        "Blood on the World’s Hands": "Blood on the World's Hands",
        "Bring Your Daughter… to the Slaughter": "Bring Your Daughter... to the Slaughter",
        "Children Of The Damned": "Children of the Damned",
        "Run To The Hills": "Run to the Hills",
        "The Number Of The Beast": "The Number of the Beast",
    }

    albums.replace(song_name_harmonization, inplace=True)

    return albums


if __name__ == "__main__":
    import json
    import os
    from pathlib import Path

    from clean_setlists_data import clean_setlists_data

    in_path = Path(Path.cwd() / "data_prep" / "data" / "json_raw")

    # Load raw JSON data
    in_songs_file = "musicbrainz_songs.json"
    with open(Path(in_path / in_songs_file), "r") as songs_file:
        albums = json.load(songs_file)

    # Run the data cleaning function
    albums = clean_album_data(albums)

    # Save the clean data to CSV
    out_path = Path.cwd() / "data_prep" / "data" / "csv"
    os.makedirs(out_path, exist_ok=True)
    albums.to_csv(Path(out_path / "albums_clean.csv"), index=False)


    # Check the song name harmonization - "filter" should only return
    # non-original songs (covers, playbacks, etc.)
    
    # Define helper function to test data cleaning
    def filter_non_album_songs(
        setlists_df: pd.DataFrame, albums_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Helper function to filter unique song names that are in the
        "setlists" table, but not in the "albums" table (covers,
        playback intros, etc.)
        """
        filter = setlists_df[~setlists_df["song_title"].isin(albums_df["song_name"])]
        filter = filter.drop_duplicates(subset="song_title")
        return filter

    # Use the clean_setlists_data() function to obtain a clean copy of
    # the setlits data
    in_setlists_file = "setlist_fm_setlists.json"
    missing_tour_data_file = "missing_tour_data.csv"
    with open(Path(in_path / in_setlists_file), "r") as setlists_file:
        setlists = json.load(setlists_file)
    missing_tour_data = pd.read_csv(Path(in_path / ".." / missing_tour_data_file))
    setlists = clean_setlists_data(setlists, missing_tour_data)

    filter = filter_non_album_songs(setlists, albums)
    print(filter)
