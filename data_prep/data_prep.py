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
    # Add missing venue information (NA = unknown venue)
    concerts_df["venue"] = concerts_df["venue"].fillna("Unknown Venue")

    # Concatenate song title and playback (tape) & cover information
    # Conditions:
    #   - from_tape == True AND cover column contains a value
    #   - from_tape == True
    #   - ONLY cover column contains a value
    condlist = [
        concerts_df["from_tape"].eq(True) & concerts["cover"].notna(),
        concerts_df["from_tape"].eq(True),
        concerts_df["cover"].notna(),
    ]

    choicelist = [
        np.where(
            concerts_df["cover"].notna(),
            concerts_df["song_title"] + " (from tape, " + concerts["cover"] + " song)",
            concerts_df["song_title"],
        ),
        concerts["song_title"] + " (from tape)",
        np.where(
            concerts_df["cover"].notna(),
            concerts_df["song_title"] + " (" + concerts["cover"] + " cover)",
            concerts_df["song_title"],
        ),
    ]

    # Apply choicelist on condlist
    concerts_df["song_title"] = np.select(
        condlist, choicelist, default=concerts_df["song_title"]
    )

    single_line_setlists = []

    # Create a single string for each setlist - determined by the id
    for id, setlist in concerts_df.groupby("id"):
        concatenated_setlist = []

        for index, row in setlist.iterrows():
            # Convert NAs (= missing song titles) to empty strings
            song_title = row["song_title"] if pd.notna(row["song_title"]) else ""
            concatenated_setlist.append(song_title)
            concatenated_setlist.append("<br>")

            # Add encore information
            if (pd.notna(row["encore"])) and (
                f"Encore {int(row["encore"])}:" not in concatenated_setlist
            ):
                concatenated_setlist.append("<b>")
                concatenated_setlist.append(f"Encore {int(row["encore"])}:")
                concatenated_setlist.append("</b>")
                concatenated_setlist.append("<br>")

        # Create single setlist string & create DataFrame from setlists
        concatenated_setlist_str = "".join(concatenated_setlist)
        single_line_setlists.append({"id": id, "song_title": concatenated_setlist_str})

    single_line_setlists_df = pd.DataFrame(single_line_setlists)

    # Delete duplicate rows by ID and insert single string setlists
    concerts_df = concerts_df.drop_duplicates(subset="id", keep="first").drop(
        columns=["song_title"]
    )
    concerts_df = concerts_df.merge(single_line_setlists_df, on="id", how="left")

    concerts_df = concerts_df.drop(
        columns=["song_count", "encore", "from_tape", "cover", "album_name"]
    )
    concerts_df = concerts_df.rename(columns={"song_title": "setlist"})

    return concerts_df


def prepare_concerts_per_city(concerts_df: pd.DataFrame) -> pd.DataFrame:
    """Creates a DataFrame containing all concerts played in each city
    without setlist information

    Args:
        concerts_df (DataFrame): the cleaned dataframe containing all
            concert information

    Returns:
        concerts_per_city (DataFrame): a DataFrame containing all
            concerts played in each city without setlist information
    """
    concerts_per_city = concerts_df.drop(
        columns=[
            "song_count",
            "song_title",
            "encore",
            "from_tape",
            "cover",
            "album_name",
        ]
    )

    concerts_per_city = concerts_per_city.drop_duplicates(subset="id", keep="first")

    return concerts_per_city


def prepare_albums_total(concerts_df: pd.DataFrame) -> pd.DataFrame:
    """Creates a DataFrame containing tour and album data for all
    concerts

    Args:
        concerts_df (DataFrame): the cleaned dataframe containing all
            concert information

    Returns:
        albums_total (DataFrame): a DataFrame containing tour and album
            data for all concerts
    """
    albums_total = concerts_df.drop(
        columns=[
            "venue",
            "city",
            "country",
            "latitude",
            "longitude",
            "song_count",
            "song_title",
            "encore",
            "from_tape",
            "cover",
        ]
    )

    # Drop duplicate IDs
    albums_total = albums_total.dropna(subset="album_name")

    return albums_total


if __name__ == "__main__":
    from pathlib import Path

    path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    concerts_file = "concerts_clean.csv"
    concerts = pd.read_csv(Path(path / concerts_file))

    setlists = prepare_setlists(concerts)
    setlists.to_csv(Path(path / "app_setlist_data.csv"), index=False, encoding="utf-8")

    concerts_per_city = prepare_concerts_per_city(concerts)
    concerts_per_city.to_csv(
        Path(path / "app_city_data.csv"), index=False, encoding="utf-8"
    )

    albums_total = prepare_albums_total(concerts)
    albums_total.to_csv(
        Path(path / "app_albums_data.csv"), index=False, encoding="utf-8"
    )
