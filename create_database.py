import pandas as pd
import json

with open("setlists.json", "r") as file:
    setlists = json.load(file)

column_names = ["concert_id", "concert_date", "tour_name", "venue_id", "venue_name", "city_id",
                "city", "state_id", "state", "country_id", "country", "latitude", "longitude",
                "setlist_id", "setlist_detail_id", "song_id", "album_id", "setlist_position",
                "song_name", "album_name", "tape", "cover_info", "encore"]

columns = {col_name: [] for col_name in column_names}

for record in setlists:
    # concert_id
    # concert_date
    # tour_name
    columns["venue_id"].append(record["venue"]["id"])
    columns["venue_name"].append(record["venue"]["name"])
    columns["city_id"].append(record["venue"]["city"]["id"])

# Create venue table
venue = pd.DataFrame(list(zip(columns["venue_id"], 
                              columns["city_id"],
                              columns["venue_name"])),
                              columns = ["venue_id", "city_id", "venue_name"])
venue = venue.drop_duplicates(subset = "venue_id", keep = "first")

print(venue)