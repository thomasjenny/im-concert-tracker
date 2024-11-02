import numpy as np
import pandas as pd


def prepare_setlists(concerts: pd.DataFrame) -> pd.DataFrame:

    # Add a value to all rows where venue is an empty string
    concerts["venue"] = concerts["venue"].fillna("Unknown Venue")

    # Convert empty strings in the cover_info column to NA
    # -------> The values are already NaN

    # print(concerts.dtypes)

    # Add tape/cover info to the song names in brackets
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

    concerts["song_title"] = np.select(
        condlist, choicelist, default=concerts["song_title"]
    )

    # Create single setlist string

    single_line_setlists = []

    for id, setlist in concerts.groupby("id"):
        # print(setlist)

        # print(id)

        concatenated_setlist = []

        for index, row in setlist.iterrows():
            song_title = row["song_title"] if pd.notna(row["song_title"]) else ""
            concatenated_setlist.append(song_title)
            concatenated_setlist.append("<br>")

            if (pd.notna(row["encore"])) and (
                f"Encore {int(row["encore"])}" not in concatenated_setlist
            ):
                concatenated_setlist.append("<b>")
                concatenated_setlist.append(f"Encore {int(row["encore"])}")
                concatenated_setlist.append("</b>")
                concatenated_setlist.append("<br>")

        concatenated_setlist_str = "".join(concatenated_setlist)

        single_line_setlists.append({"id": id, "song_title": concatenated_setlist_str})

        # print(concatenated_setlist_str)
        # print(single_line_setlists)

        # break

    single_line_setlists_df = pd.DataFrame(single_line_setlists)

    # Delete all rows except 1 per ID and delete the song_title colum
    concerts = concerts.drop_duplicates(subset="id", keep="first").drop(
        columns=["song_title"]
    )
    concerts = concerts.merge(single_line_setlists_df, on="id", how="left")

    # Delete columns that are not needed anymore
    concerts = concerts.drop(
        columns=["song_count", "encore", "from_tape", "cover", "album_name"]
    )
    concerts = concerts.rename(columns={"song_title": "setlist"})

    return concerts


# 1 file with all concerts per city --> if "All Tours"
# is selected, the tooltip should show every concert
# in the city instead of a setlist.


def prepare_concerts_per_city(concerts: pd.DataFrame) -> pd.DataFrame:
    """docstring
    TAKE OUTPUT FROM THE PREVIOUS FUNCTION!!!!
    """
    concerts_per_city = concerts.drop(
        columns=[
            "song_count",
            "song_title",
            "encore",
            "from_tape",
            "cover",
            "album_name",
        ]
    )

    # Drop duplicate IDs
    concerts_per_city = concerts_per_city.drop_duplicates(subset="id", keep="first")

    return concerts_per_city


#
# 1 file with all the albums played per concert
# for the album viz --> must enable analysis for single
# concert and all concerts together (all tours)
#
def albums():
    pass

def prepare_albums_total(concerts: pd.DataFrame) -> pd.DataFrame:
    """docstring
    TAKE OUTPUT FROM THE PREVIOUS FUNCTION!!!!
    """
    albums_total = concerts.drop(
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
    albums_total = albums_total.dropna(subset = "album_name")

    return albums_total


if __name__ == "__main__":
    from pathlib import Path

    path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    concerts_file = "concerts_clean.csv"
    concerts = pd.read_csv(Path(path / concerts_file))

    # setlists = prepare_setlists(concerts)
    # concerts.to_csv(Path(path / "app_setlist_data.csv"), index=False)

    # concerts_per_city = prepare_concerts_per_city(concerts)
    # concerts_per_city.to_csv(Path(path / "app_city_data.csv"))

    albums_total = prepare_albums_total(concerts)
    print(albums_total)
    
