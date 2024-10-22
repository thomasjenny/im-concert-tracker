import pandas as pd
import json
import os
from typing import List


def create_concert_venue_city_tables(setlists: List[dict]) -> pd.DataFrame:
    """Create concert, venue, and city tables from the setlist data
    returned by the setlist.fm API.

    Args:
        setlists (list): list of all concerts fetched from the API

    Returns:
        concert (dataframe): concert table in pandas dataframe format
        venue (dataframe): venue table in pandas dataframe format
        city (dataframe): city table in pandas dataframe format
    """
    column_names = [
        "concert_id",
        "date",
        "tour",
        "venue_id",
        "venue",
        "city_id",
        "city",
        "country_id",
        "country",
        "latitude",
        "longitude",
    ]

    columns = {col_name: [] for col_name in column_names}

    for record in setlists:
        columns["concert_id"].append(record.get("id", None))
        columns["date"].append(record.get("eventDate", None))
        columns["tour"].append(record.get("tour", {}).get("name", None))
        columns["venue_id"].append(record.get("venue", {}).get("id", None))
        columns["venue"].append(record.get("venue", {}).get("name", None))
        columns["city_id"].append(
            record.get("venue", {}).get("city", {}).get("id", None)
        )

        city = record.get("venue", {}).get("city", {}).get("name", None)
        country_id = (
            record.get("venue", {}).get("city", {}).get("country", {}).get("code", None)
        )
        state = record.get("venue", {}).get("city", {}).get("stateCode", None)
        if (country_id == "US") and (state != None):
            columns["city"].append(f"{city}, {state}")
        else:
            columns["city"].append(city)

        columns["country_id"].append(country_id)
        columns["country"].append(
            record.get("venue", {}).get("city", {}).get("country", {}).get("name", None)
        )
        columns["latitude"].append(
            record.get("venue", {}).get("city", {}).get("coords", {}).get("lat", None)
        )
        columns["longitude"].append(
            record.get("venue", {}).get("city", {}).get("coords", {}).get("long", None)
        )

    # Create concert table
    concert = pd.DataFrame(
        list(
            zip(
                columns["concert_id"],
                columns["venue_id"],
                columns["city_id"],
                columns["date"],
                columns["tour"],
            )
        ),
        columns=["concert_id", "venue_id", "city_id", "date", "tour"],
    )
    concert = concert.drop_duplicates(subset="concert_id", keep="first")

    # Create venue table
    venue = pd.DataFrame(
        list(zip(columns["venue_id"], columns["city_id"], columns["venue"])),
        columns=["venue_id", "city_id", "venue"],
    )
    venue = venue.drop_duplicates(subset="venue_id", keep="first")

    # Create city table
    city = pd.DataFrame(
        list(
            zip(
                columns["city_id"],
                columns["city"],
                columns["country_id"],
                columns["country"],
                columns["latitude"],
                columns["longitude"],
            )
        ),
        columns=["city_id", "city", "country_id", "country", "latitude", "longitude"],
    )
    city = city.drop_duplicates(subset="city_id", keep="first")

    return concert, venue, city


def create_setlist_table(setlists: List[dict]) -> pd.DataFrame:
    """Create the setlist table from the setlist data returned by the
    setlist.fm API.

    Args:
        setlists (list): list of all concerts fetched from the API

    Returns:
        setlist (dataframe): setlist table in pandas dataframe format
    """
    column_names = [
        "setlist_id",
        "concert_id",
        "setlist_position",
        "song_name",
        "album_name",
        "tape",
        "cover_info",
        "encore",
    ]

    columns = {col_name: [] for col_name in column_names}

    for record in setlists:
        sets = record.get("sets", {}).get("set", {})

        # Counter must be here to reset after each concert - further down, it would reset after each set.
        setlist_position_counter = 1

        for set in sets:
            songs = set["song"]

            for song in songs:
                columns["setlist_id"].append(
                    f"{record.get("id")}_{setlist_position_counter}"
                )
                columns["concert_id"].append(record.get("id"))
                # prevent empty song titles from being added to the table
                if song.get("name", "") != "":
                    columns["song_name"].append(song.get("name"))
                columns["setlist_position"].append(setlist_position_counter)
                columns["encore"].append(bool(set.get("encore", 0)))
                columns["tape"].append(song.get("tape", False))
                columns["cover_info"].append(song.get("cover", {}).get("name", ""))

                setlist_position_counter += 1

    setlist = pd.DataFrame(
        list(
            zip(
                columns["setlist_id"],
                columns["concert_id"],
                columns["song_name"],
                columns["setlist_position"],
                columns["cover_info"],
                columns["encore"],
                columns["tape"],
            )
        ),
        columns=[
            "setlist_id",
            "concert_id",
            "song_name",
            "setlist_position",
            "cover_info",
            "encore",
            "tape",
        ],
    )

    return setlist


def create_albums_table(releases: List[dict]) -> pd.DataFrame:
    """Create the albums table from the releases data returned by the
    Musicbrainz API.

    Args:
        releases (list): list of all releases fetched from the API

    Returns:
        albums (dataframe): albums table in pandas dataframe format
    """
    column_names = [
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
                columns["song_name"].append(track.get("title"))

    albums = pd.DataFrame(
        list(
            zip(
                columns["album_name"],
                columns["song_name"],
            )
        ),
        columns=[
            "album_name",
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
    with open("setlists.json", "r") as file:
        setlists = json.load(file)

    with open("./test/songs_test.json") as file:
        albums = json.load(file)

    concert, venue, city = create_concert_venue_city_tables(setlists)
    setlist = create_setlist_table(setlists)
    albums = create_albums_table(albums)

    # Optional: write to CSV
    # os.makedirs("data", exist_ok=True)
    # concert.to_csv("data/concert.csv", index=False, encoding="utf-8")
    # venue.to_csv("data/venue.csv", index=False, encoding="utf-8")
    # city.to_csv("data/city.csv", index=False, encoding="utf-8")
    # setlist.to_csv("data/setlist.csv", index=False, encoding="utf-8")
    # albums.to_csv("data/albums.csv", index=False, encoding="utf-8")
