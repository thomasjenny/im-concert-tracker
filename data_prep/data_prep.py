import numpy as np
import pandas as pd


def prepare_setlists(concerts: pd.DataFrame) -> pd.DataFrame:

    # Add a value to all rows where venue is an empty string
    concerts["venue"] = concerts["venue"].fillna("Unknown Venue")
    
    # Convert empty strings in the cover_info column to NA
    # -------> The values are already NaN

    print(concerts.dtypes)

    # Add tape/cover info to the song names in brackets
    condlist = [
         concerts["from_tape"].eq(True) & concerts["cover"].notna(),
         concerts["from_tape"].eq(True),
         concerts["cover"].notna()
    ]

    choicelist = [
        np.where(
            concerts["cover"].notna(),
            concerts["song_title"] + " (from tape, " + concerts["cover"] + " song)",
            concerts["song_title"]
        ),
        concerts["song_title"] + " (from tape)",
        np.where(concerts["cover"].notna(),
                 concerts["song_title"] + " (" + concerts['cover'] + " cover)",
                 concerts["song_title"]
        )
    ]
    
    concerts["song_title"] = np.select(condlist, choicelist, default=concerts["song_title"])


    # Concatenate setlist order numbers and song titles (e.g., 1. The Evil That Men Do)
    # Loop through each concert (by unique concert index)
    # Replace all encore numbers, but keep the first one
    # put song titles in a list. if encore = 1, 2, etc., add this in between
    # re-create the dataframe

    return concerts


# 1 file with all concerts per city --> if "All Tours"
# is selected, the tooltip should show every concert
# in the city instead of a setlist.

def concerts_per_city():
    pass

#
# 1 file with all the albums played per concert
# for the album viz --> must enable analysis for single
# concert and all concerts together (all tours)
#
def albums():
    pass


if __name__ == "__main__":
    from pathlib import Path

    path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    concerts_file = "concerts.csv"
    concerts = pd.read_csv(Path(path / concerts_file))

    concerts = prepare_setlists(concerts)
    
    concerts.to_csv(Path(path / "app_test.csv"), index=False)
