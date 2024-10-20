import pandas as pd
import json

with open("setlists.json", "r") as file:
    setlists = json.load(file)

# print(type(setlists))
# print((setlists[0]["venue"]))

venue_id, city_id, venue_name = [], [], []

for i in setlists:
    individual_venue_id = i["venue"]["id"]
    individual_city_id = i["venue"]["city"]["id"]
    individual_venue_name = i["venue"]["name"]

    venue_id.append(individual_venue_id)
    city_id.append(individual_city_id)
    venue_name.append(individual_venue_name)

print(len(venue_id))
print(len(city_id))
print(len(venue_name))