import os
import requests
import math
import time
import pprint
import json

def get_setlists(mbid, headers):
    """
    """
    base_request = f"https://api.setlist.fm/rest/1.0/artist/{mbid}/setlists"
    more_results_available = True
    page = 1
    setlists = []

    while more_results_available:
        request = f"{base_request}?p={page}"
        response = requests.get(request, headers = headers).json()
        setlists.extend(response["setlist"])

        total_items = response["total"]
        items_per_page = response["itemsPerPage"]
        number_of_pages = math.ceil(total_items / items_per_page)
        if page % 5 == 0:
            print(f"Page {page} of {number_of_pages} total pages queried.")
        page += 1
        time.sleep(2)

        if page >= number_of_pages:
            more_results_available = False

    # page_numbers_request = f"https://api.setlist.fm/rest/1.0/artist/{mbid}/setlists?p=1"
    # page_numbers_response = requests.get(page_numbers_request, headers = headers).json()
    # total_items = page_numbers_response["total"]
    # items_per_page = page_numbers_response["itemsPerPage"]
    # total_pages = math.ceil(total_items / items_per_page)
    # setlists = []

    # print(f"Attempting to fetch {total_items} items from {total_pages} pages.")
# 
    # for page in range(1, total_pages + 1):
    #     request = f"https://api.setlist.fm/rest/1.0/artist/{mbid}/setlists?p={page}"
    #     response = requests.get(request, headers = headers).json()
    #     setlists.extend(response["setlist"])
    #     time.sleep(2)
    #     if page % 5 == 0:
    #         print(f"Page {page} of {total_pages} queried.")
    
    return setlists


if __name__ == "__main__":
    API_KEY = os.getenv('api_key')
    headers = {"x-api-key": API_KEY,
               "Accept": "application/json",
               "Accept-Languate": "en"}
    mbid = "ca891d65-d9b0-4258-89f7-e6ba29d83767" # MBID for Iron Maiden
    
    setlists = get_setlists(mbid, headers)
    pprint.pp(setlists[:3])

    with open("setlists_test_new.json", "w") as file:
        json.dump(setlists, file, indent = 4) 

    