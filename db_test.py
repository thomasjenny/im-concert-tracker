from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

db_in_path = Path.cwd() / "data" / "db"
db_in_name = "iron_maiden_concerts.db"
engine = create_engine(f"sqlite:///{db_in_path}/{db_in_name}", echo=True)

test_sql_statement = """
SELECT
    concert.concert_id
    ,concert.date
    ,city.city
    ,city.country
    ,venue.venue
    ,setlist.setlist_position
    ,setlist.song_name
    ,album.album_name
    ,setlist.tape
    ,setlist.cover_info
    ,setlist.encore
    ,concert.tour
    ,city.latitude
    ,city.longitude
FROM concert
LEFT JOIN venue ON concert.venue_id = venue.venue_id
LEFT JOIN city ON concert.city_id = city.city_id
LEFT JOIN setlist ON concert.concert_id = setlist.concert_id
LEFT JOIN album ON setlist.song_name = album.song_name
ORDER BY 
    SUBSTR(date, 7, 4) || '-' ||  -- Year
    SUBSTR(date, 4, 2) || '-' ||  -- Month
    SUBSTR(date, 1, 2) DESC       -- Day DESC, 
    ,setlist_position ASC
;
"""

with engine.begin() as conn:
    # city_test = pd.read_sql("SELECT * FROM city;", engine)
    # test = pd.read_sql("SELECT song_name FROM setlist;", engine)
    test = pd.read_sql(test_sql_statement, engine)

print(test)
