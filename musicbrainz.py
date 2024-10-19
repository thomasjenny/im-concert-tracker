import requests
import time
import pprint

def get_releases(mbid):
    """Fetch releases from the Musicbrainz API with pagination support. 
    Currently set to only fetch official album releases.

    Args:
        mbid (str): Musicbrainz ID of any given artist
    
    Returns:
        releases (list): list of all releases fetched from the API
    """
    base_request = f"https://musicbrainz.org/ws/2/release?artist={mbid}&type=album&status=official&fmt=json"
    offset = 0
    limit = 100
    more_results_available = True
    releases = []

    while more_results_available:
        request = f"{base_request}&limit={limit}&offset={offset}"
        response = requests.get(request).json()
        releases.extend(response["releases"])

        release_count = response["release-count"]
        print(f"Results {offset}-{len(releases)} of {release_count} total results queried.")
        offset += limit
        time.sleep(1)

        if offset >= release_count:
            more_results_available = False

    return releases


if __name__ == "__main__":
    mbid = "ca891d65-d9b0-4258-89f7-e6ba29d83767" # MBID for Iron Maiden
    releases = get_releases(mbid)
    pprint.pp(releases[:3])