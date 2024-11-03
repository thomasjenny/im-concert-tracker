import time
from typing import List

import requests


def get_releases(mbid: str) -> List[dict]:
    """Fetch releases for an artist MBID from the Musicbrainz API with
    pagination support. Currently set to only fetch official album
    releases.

    Args:
        mbid (str): Musicbrainz ID of any given artist

    Returns:
        releases (list): list of all releases fetched from the API
    """
    print(f"Querying releases for artist mbid {mbid}...")
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
        print(
            f"Results {offset}-{len(releases)} of {release_count} total results queried."
        )
        offset += limit

        if offset >= release_count:
            more_results_available = False

        time.sleep(1)

    return releases


def get_songs(releases: List[dict], test: bool = False) -> List[dict]:
    """Fetch songs from the Musicbrainz API. Uses the output of
    get_releases() to extract all release MBIDs and query all songs for
    each release.

    Args:
        releases (list): list of releases containing a dictionary which
            must contain at least a key-value pair of {"id": "<mbid>"}
            at the top level

    Returns:
        songs (list): list of all songs for the input releases fetched
            from the API
    """
    print(f"Querying songs...")
    songs = []

    for index, release in enumerate(releases):
        release_mbid = release["id"]
        request = f"https://musicbrainz.org/ws/2/release/{release_mbid}?inc=recordings&fmt=json"
        response = requests.get(request).json()
        songs.extend([response])

        if (index == 1) or (index % 20 == 0 and index != 0):
            print(f"Release {index} of {len(releases)} total releases queried.")
        elif index + 1 == len(releases):
            print(f"Release {index + 1} of {len(releases)} total releases queried.")

        if (test == True) and (index == 4):
            break

        time.sleep(1)

    return songs


if __name__ == "__main__":
    import json
    import os
    from pathlib import Path
    import pprint

    mbid = "ca891d65-d9b0-4258-89f7-e6ba29d83767"  # MBID for Iron Maiden

    # Test get_releases
    releases = get_releases(mbid)
    pprint.pp(releases[0])
    print(len(releases))

    print(f"\n\n{99 * '='}\n\n")  # Delimiter

    # Test get_songs
    songs = get_songs(releases)
    pprint.pp(songs[0])
    print(len(songs))

    # Write test results to JSON file
    out_path = Path.cwd() / "data_prep" / "data" / "json_raw"
    os.makedirs(out_path, exist_ok=True)
    out_filename_releases = "musicbrainz_releases.json"
    out_filename_songs = "musicbrainz_songs.json"

    with open(Path(out_path, out_filename_releases), "w") as releases_file:
        json.dump(releases, releases_file, indent=4)
    with open(Path(out_path, out_filename_songs), "w") as songs_file:
        json.dump(songs, songs_file, indent=4)
