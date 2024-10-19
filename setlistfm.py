import os
import requests
import math
import time
import pprint
import json

def get_setlists(mbid, headers, page_limit = None):
    """Fetch concerts from the setlist.fm API.

    Args:
        mbid (str): Musicbrainz ID of any given artist
        headers (dict): API headers
        page_limit (optional, int): maximum number of pages to query. If
            unspecified, all pages are queried.

    Returns:
        setlists (list): list of all concerts fetched from the API
    """
    print(f"Querying setlist information for artist mbid {mbid}.")
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

        if page_limit and page >= page_limit:
            more_results_available = False
            print(f"Page {page} of {number_of_pages} total pages queried.")

        if page >= number_of_pages:
            more_results_available = False

        page += 1
        time.sleep(2)
    
    return setlists


if __name__ == "__main__":
    API_KEY = os.getenv('api_key')
    headers = {"x-api-key": API_KEY,
               "Accept": "application/json",
               "Accept-Languate": "en"}
    mbid = "ca891d65-d9b0-4258-89f7-e6ba29d83767" # MBID for Iron Maiden
    
    setlists = get_setlists(mbid, headers, 1)
    pprint.pp(setlists[:2])

    