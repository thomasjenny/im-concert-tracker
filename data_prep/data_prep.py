from pathlib import Path

import numpy as np
import pandas as pd


# Requirements:
# 1 file with the following structure:
# 1 line per concert
#   - concert_id
#   - date
#   - venue
#   - city
#   - latitude
#   - longitude
#   - country
#   - tour
#   - song_name --> all song names in 1 line, separated by <br>
#


def prepare_data_for_app(concerts: pd.DataFrame) -> pd.DataFrame:
    pass






# 1 file with all concerts per city --> if "All Tours"
# is selected, the tooltip should show every concert
# in the city instead of a setlist.
#
# 1 file with all the albums played per concert
# for the album viz --> must enable analysis for single
# concert and all concerts together (all tours)
#




# print(setlists)

# Add a value to all rows where album_name is NA (i.e., non-original songs)
# --> should not be required --> filter out all NAs in App.

# Add a value to all rows where venue is an empty string
# print(setlists.loc[setlists["venue"] == ""])
setlists["venue"] = setlists["venue"].replace("", "Unkown Venue")
# print(setlists.loc[setlists["venue"] == ""])


# Convert empty strings in the cover_info column to NA
# print(setlists)
# print(setlists.loc[setlists["cover_info"] != "NA"])
setlists["cover_info"] = setlists["cover_info"].replace("", "NA")
# print(setlists.loc[setlists["cover_info"] != "NA"])

print(setlists)
# Add tape/cover info to the song names in brackets
# song_conditions = [
#      setlists["tape"].eq("True") & setlists["cover_info"].no
# ]

setlists.to_csv("testdata/test_setlist.csv")


    #   mutate(
    #     song_name = case_when(
    #       tape == 1 & !is.na(cover_info) ~ paste0(song_name, " (from tape, oringinally by ", cover_info, ")"),
    #       tape == 1 ~ paste0 (song_name, " (from tape"),
    #       !is.na(cover_info) ~ paste0(song_name, " (", cover_info, " cover)"),
    #       TRUE ~ song_name
    #     )
#       ) %>%
#       
#       # Concatenate setlist order numbers and song titles (e.g., 1. The Evil That Men Do)
