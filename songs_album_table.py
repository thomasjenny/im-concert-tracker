import pandas as pd
import json
import os
import pprint
import create_database

##############
## MOVE THIS TO create_database.py
##############


def albums_test(releases):
    """Create the albums table from the releases data returned by the
    Musicbrainz API.

    Args:
        releases (list): list of all releases fetched from the API

    Returns:
        albums (dataframe): albums table in pandas dataframe format
    """
    column_names = [
        # "track_position",
        "song_name",
        "album_name",
    ]

    columns = {col_name: [] for col_name in column_names}

    for release in releases:
        # Media contains the track information
        for media in release.get("media"):
            # tracks is a list of dicts containing song information
            for track in media.get("tracks"):
                # Album name is in the top-level dict
                columns["album_name"].append(release.get("title"))
                # columns["track_position"].append(track.get("position"))
                columns["song_name"].append(track.get("title"))

    albums = pd.DataFrame(
        list(
            zip(
                columns["album_name"],
                # columns["track_position"],
                columns["song_name"],
            )
        ),
        columns=[
            "album_name",
            # "track_position",
            "song_name",
        ],
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
    albums.sort_values(by=["album_name"])

    return albums


if __name__ == "__main__":
    # with open("setlists.json", "r") as file:
    #     # with open("single_setlist.json", "r") as file:
    #     setlists = json.load(file)

    # df = create_database.create_setlist_table(setlists)
    # print(df)
    # print(type(df))

    with open("./test/songs_test.json") as file:
        albums = json.load(file)
    albums = albums_test(albums)
    print(albums)

    # Write to CSV
    os.makedirs("data", exist_ok=True)
    albums.to_csv("data/albums.csv", index=False, encoding="utf-8")
