from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

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
# 1 file with all concerts per city --> if "All Tours"
# is selected, the tooltip should show every concert
# in the city instead of a setlist.
#
# 1 file with all the albums played per concert
# for the album viz --> must enable analysis for single
# concert and all concerts together (all tours)
#

# SQL Command:
sql_statement = """
SELECT
    concert.concert_id
    ,concert.date
    ,venue.venue
    ,city.city
    ,city.latitude
    ,city.longitude
    ,city.country
    ,concert.tour
    ,setlist.setlist_position
    ,setlist.song_name
    ,album.album_name
    ,setlist.tape
    ,setlist.cover_info
    ,setlist.encore
FROM concert
LEFT JOIN venue ON concert.venue_id = venue.venue_id
LEFT JOIN city ON concert.city_id = city.city_id
LEFT JOIN setlist ON concert.concert_id = setlist.concert_id
LEFT JOIN album ON setlist.song_name = album.song_name
ORDER BY 
    SUBSTR(date, 7, 4) || '-' ||  -- Year
    SUBSTR(date, 4, 2) || '-' ||  -- Month
    SUBSTR(date, 1, 2) DESC       -- Day DESC
    ,setlist_position ASC
;
"""

dtypes = {
    "concert_id": pd.StringDtype(),
    "date": pd.StringDtype(),
    "venue": pd.StringDtype(),
    "city": pd.StringDtype(),
    "latitude": pd.StringDtype(),
    "longitude": pd.StringDtype(),
    "country": pd.StringDtype(),
    "tour": pd.StringDtype(),
    "setlist_position": pd.Int32Dtype(),
    "song_name": pd.StringDtype(),
    "album_name": pd.StringDtype(),
    "tape": pd.BooleanDtype(),
    "cover_info": pd.StringDtype(),
    "encore": pd.Int32Dtype(),
}

db_in_path = Path.cwd() / "data" / "db"
db_in_name = "iron_maiden_concerts.db"
engine = create_engine(f"sqlite:///{db_in_path}/{db_in_name}", echo=False)

with engine.begin() as conn:
    setlists = pd.read_sql(sql_statement, conn, dtype=dtypes)

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
