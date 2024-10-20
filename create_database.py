import pandas as pd
import json

with open("setlists.json", "r") as file:
    setlists = json.load(file)

column_names = ["concert_id", "date", "tour", "venue_id", "venue", "city_id", "city", 
                "country_id", "country", "latitude", "longitude",
                "setlist_id", "setlist_detail_id", "song_id", "album_id", "setlist_position",
                "song_name", "album_name", "tape", "cover_info", "encore"]

columns = {col_name: [] for col_name in column_names}

for record in setlists:
    columns["concert_id"].append(record.get("id", None))
    columns["date"].append(record.get("eventDate", None))
    columns["tour"].append(record.get("tour", {}).get("name", None))
    columns["venue_id"].append(record.get("venue", {}).get("id", None))
    columns["venue"].append(record.get("venue", {}).get("name", None))
    columns["city_id"].append(record.get("venue", {}).get("city", {}).get("id", None))
    
    city = record.get("venue", {}).get("city", {}).get("name", None)
    country_id = record.get("venue", {}).get("city", {}).get("country", {}).get("code", None)
    state = record.get("venue", {}).get("city", {}).get("stateCode", None)
    if (country_id == "US") and (state != None):
        columns["city"].append(f"{city}, {state}")
    else:
        columns["city"].append(city)
    
    columns["country_id"].append(country_id)
    columns["country"].append(record.get("venue", {}).get("city", {}).get("country", {})
                              .get("name", None))
    columns["latitude"].append(record.get("venue", {}).get("city", {}).get("coords", {})
                              .get("lat", None))
    columns["longitude"].append(record.get("venue", {}).get("city", {}).get("coords", {})
                              .get("long", None))



print(columns["longitude"])

# for record in setlists:
#     if record.get("venue", {}).get("city", {}).get("country", {}).get("code", None) == "US":
#         print(f"{record.get("venue", {}).get("city", {}).get("name", None)}, "
#               f"{record.get("venue", {}).get("city", {}).get("stateCode", None)}"
#                                           )

# # Create concert table
# concert = pd.DataFrame(list(zip(columns["concert_id"],
#                                 columns["venue_id"],
#                                 columns["city_id"],
#                                 columns["date"],
#                                 columns["tour"])),
#                                 columns = ["concert_id", "venue_id", "city_id", "date", "tour"])
# concert = concert.drop_duplicates(subset = "concert_id", keep = "first")
# 
# # Create venue table
# venue = pd.DataFrame(list(zip(columns["venue_id"], 
#                               columns["city_id"],
#                               columns["venue"])),
#                               columns = ["venue_id", "city_id", "venue"])
# venue = venue.drop_duplicates(subset = "venue_id", keep = "first")
# 
# # Create city table
# city = pd.DataFrame(list(zip(columns)))
# 
# print(venue)