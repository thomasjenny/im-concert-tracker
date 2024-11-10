import numpy as np
import pandas as pd


def prepare_setlists(concerts_df: pd.DataFrame) -> pd.DataFrame:
    """Prepares the concerts data (i.e., the joined setlist.fm setlists
    and musicbrainz albums data) to provide concatenated setlist
    information for each concert to be used in the Shiny app. Requires
    a DataFrame with the following columns:
    id, date, venue, city, country, latitude, longitude, tour,
    song_count, song_title, encore, from_tape, cover, album_name

    Args:
        concerts_df (DataFrame): the cleaned dataframe containing all
            concert information

    Returns:
        concerts_df (DataFrame): the transformed concerts DataFrame.
            Transformations include data cleaning, the concatenation of
            song, tape, and cover information, and the concatenation of
            all songs into a single string to be used in the Shiny app
    """
    # Create a copy of the original DataFrame
    concerts = concerts_df.copy(deep=True)

    # Add missing venue information (NA = unknown venue)
    concerts["venue"] = concerts["venue"].fillna("Unknown Venue")

    # Concatenate song title and playback (tape) & cover information
    # Conditions:
    #   - from_tape == True AND cover column contains a value
    #   - from_tape == True
    #   - ONLY cover column contains a value
    condlist = [
        concerts["from_tape"].eq(True) & concerts["cover"].notna(),
        concerts["from_tape"].eq(True),
        concerts["cover"].notna(),
    ]

    choicelist = [
        np.where(
            concerts["cover"].notna(),
            concerts["song_title"] + " (from tape, " + concerts["cover"] + " song)",
            concerts["song_title"],
        ),
        concerts["song_title"] + " (from tape)",
        np.where(
            concerts["cover"].notna(),
            concerts["song_title"] + " (" + concerts["cover"] + " cover)",
            concerts["song_title"],
        ),
    ]

    # Apply choicelist on condlist
    concerts["song_title"] = np.select(
        condlist, choicelist, default=concerts["song_title"]
    )

    # Concatenate setlist position and song title
    concerts["song_title"] = (
        concerts["song_count"].astype(str) + ". " + concerts["song_title"].astype(str)
    )

    single_line_setlists = []

    # Create a single string for each setlist - determined by the id
    for id, setlist in concerts.groupby("id"):
        concatenated_setlist = []

        for index, row in setlist.iterrows():
            # Convert NAs (= missing song titles) to empty strings
            song_title = row["song_title"] if pd.notna(row["song_title"]) else ""
            concatenated_setlist.append(song_title)

            # Add encore information
            if (pd.notna(row["encore"])) and (
                f"Encore {int(row["encore"])}:" not in concatenated_setlist
            ):
                # pop is required to ensure correct order of encore
                # list elements
                first_encore_song = concatenated_setlist.pop()
                concatenated_setlist.append("<b>")
                concatenated_setlist.append(f"Encore {int(row["encore"])}:")
                concatenated_setlist.append("</b>")
                concatenated_setlist.append("<br>")
                concatenated_setlist.append(first_encore_song)

            concatenated_setlist.append("<br>")

        # Create single setlist string & create DataFrame from setlists
        concatenated_setlist_str = "".join(concatenated_setlist)
        single_line_setlists.append({"id": id, "song_title": concatenated_setlist_str})

    single_line_setlists_df = pd.DataFrame(single_line_setlists)

    # Delete duplicate rows by ID and insert single string setlists
    concerts = concerts.drop_duplicates(subset="id", keep="first").drop(
        columns=["song_title"]
    )
    concerts = concerts.merge(single_line_setlists_df, on="id", how="left")

    concerts = concerts.drop(
        columns=["song_count", "encore", "from_tape", "cover", "album_name"]
    )
    concerts = concerts.rename(columns={"song_title": "setlist"})

    return concerts


def prepare_albums_songs_played(concerts_df: pd.DataFrame) -> pd.DataFrame:
    """Creates a DataFrame containing tour and album data for all
    concerts

    Args:
        concerts_df (DataFrame): the cleaned dataframe containing all
            concert information

    Returns:
        albums_total (DataFrame): a DataFrame containing tour and album
            data for all concerts
    """
    albums_songs_played = concerts_df.copy(deep=True)

    albums_songs_played = albums_songs_played.drop(
        columns=[
            "venue",
            "city",
            "country",
            "latitude",
            "longitude",
            "song_count",
            "encore",
            "from_tape",
            "cover",
        ]
    )

    # Drop all rows that don't have an album (covers, playbacks, etc.)
    albums_songs_played = albums_songs_played.dropna(subset="album_name")

    return albums_songs_played


if __name__ == "__main__":
    from pathlib import Path

    path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    concerts_file = "concerts_clean.csv"
    concerts = pd.read_csv(Path(path / concerts_file))

    setlists = prepare_setlists(concerts)
    setlists.to_csv(Path(path / "app_setlist_data.csv"), index=False, encoding="utf-8")

    albums_songs_total = prepare_albums_songs_played(concerts)
    albums_songs_total.to_csv(
        Path(path / "app_albums_songs.csv"), index=False, encoding="utf-8"
    )
