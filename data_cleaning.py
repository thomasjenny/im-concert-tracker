import pandas as pd
import os


def clean_album_table(album_table: pd.DataFrame) -> pd.DataFrame:
    """Change the song names in the albums table that differ from the
    setlists table (different capitalization or apostrophes).

    Args:
        album_table (dataframe): the albums table

    Returns:
        album_table (dataframe): the cleaned albums table
    """
    # Harmonize song names
    replacement_mapping_dict = {
        "Blood on the World’s Hands": "Blood on the World's Hands",
        "Bring Your Daughter… to the Slaughter": "Bring Your Daughter... to the Slaughter",
        "Children Of The Damned": "Children of the Damned",
        "Run To The Hills": "Run to the Hills",
        "The Number Of The Beast": "The Number of the Beast",
    }
    album_table.replace(replacement_mapping_dict, inplace=True)

    # Add "Total Eclipse" and the corresponding album
    new_row = pd.Series(
        {"album_name": "The Number of the Beast", "song_name": "Total Eclipse"},
    )
    album_table = pd.concat([album_table, new_row.to_frame().T], ignore_index=True)

    return album_table


def clean_setlist_table(setlist_table: pd.DataFrame) -> pd.DataFrame:
    """Change the song names in the albums table that differ from the
    setlists table (different capitalization or apostrophes).

    Args:
        setlist_table (dataframe): the setlist table

    Returns:
        setlist_table (dataframe): the cleaned setlist table
    """
    # Harmonize song names
    replacement_mapping_dict = {
        "633 Squadron": '"633 Squadron" Theme',
        "633 Squadron Theme": '"633 Squadron" Theme',
        'Intro - "633 Squadron" theme': '"633 Squadron" Theme',
        "Intro - 633 Squadron music": '"633 Squadron" Theme',
        'Theme from "633 Squadron"': '"633 Squadron" Theme',
        "Always Look on the Bright Side": "Always Look on the Bright Side of Life",
        "Blade Runner": "Blade Runner (End Titles)",
        "Blade Runner (end titles)": "Blade Runner (End Titles)",
        "Blade Runner Intro": "Blade Runner (End Titles)",
        "Blade Runner Soundtrack": "Blade Runner (End Titles)",
        "Bladerunner Theme": "Blade Runner (End Titles)",
        "Churchill Speech": "Churchill's Speech",
        "Churchill’s Speech": "Churchill's Speech",
        "Intro - Churchill's Speech": "Churchill's Speech",
        "Intro: Churchill's Speech": "Churchill's Speech",
        'Intro - Main Title from the movie "Where Eagles Dare"': '"Main Title" from "Where Eagles Dare"',
        "Where Eagles Dare Main Theme": '"Main Title" from "Where Eagles Dare"',
        "Where Eagles Dare Theme": '"Main Title" from "Where Eagles Dare"',
        "Mars, The Bringer of War": "Mars, the Bringer of War",
    }
    setlist_table.replace(replacement_mapping_dict, inplace=True)

    return setlist_table


def add_missing_tours(
    concert_table: pd.DataFrame, data_completion_file_path: str
) -> pd.DataFrame:
    """Add the names of the tours that are missing in the setlist.fm
    data. This function uses a local CSV file that contains the missing
    tour information. This file was created manually using a copy of the
    concert table where the "tour" value is empty. Only concert dates
    before 2003 have missing tour values, so it is expected that future
    additions to the data set will be complete and this is the most
    stable solution.

    Args:
        concert_table (dataframe): the albums table

    Returns:
        albums_table_clean (dataframe): the cleaned albums table
    """
    # Read the data completion file
    data_completion_df = pd.read_csv(data_completion_file_path)

    # Set index for both dataframes to "date" and map on date
    concert_table.set_index("date", inplace=True)
    data_completion_df.set_index("date", inplace=True)
    concert_table.update(data_completion_df)
    concert_table.reset_index(inplace=True)

    return concert_table


if __name__ == "__main__":
    # Test albums and setlists cleaning functions
    albums = pd.read_csv("data/albums.csv")
    setlists = pd.read_csv("data/setlist.csv")

    def filter_non_album_songs(
        setlists_df: pd.DataFrame, albums_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Helper function to filter unique song names that are in the
        "setlists" table, but not in the "albums" table
        """
        filter = setlists_df[~setlists_df["song_name"].isin(albums_df["song_name"])]
        filter = filter.drop_duplicates(subset="song_name")
        return filter

    # Test if studio album songs have been renamed in the "albums" table
    # to reflect the "setlists" table
    albums_clean = clean_album_table(albums)
    filter_albums_before = filter_non_album_songs(setlists, albums)
    filter_albums_after = filter_non_album_songs(setlists, albums_clean)

    # Test if duplicates in the "setlists" table of non-Maiden songs
    # have been renamed correctly
    setlists_clean = clean_setlist_table(setlists)
    filter_setlists_after = filter_non_album_songs(setlists_clean, albums_clean)

    print(
        f"{150 * "="}\n\n",
        f'Filtered raw "setlists" table - all songs in "setlists" table, but not in "albums" table:'
        f"\n{filter_albums_before}",
        f"\n\n{150 * "="}\n\n",
        f'Filtered "setlists" table after cleaning the "albums" table: \n{filter_albums_after}',
        f"\n\n{150 * "="}\n\n",
        f'Filtered "setlists" table after cleaning the "setlists" table: \n{filter_setlists_after}',
        f"\n\n{150 * "="}\n\n",
        f"Shape of filter after first cleaning step: {filter_albums_before.shape}\n",
        f"Shape of filter after second cleaning step: {filter_albums_after.shape}\n",
        f"Shape of filter after third cleaning step: {filter_setlists_after.shape}",
        f"\n\n{150 * "="}\n",
    )

    # Test tour data completion function
    data_completion_file = "./data/tour_info_completion.csv"
    concert = pd.read_csv("data/concert.csv")
    concert_clean = add_missing_tours(concert, data_completion_file)
    print(concert_clean)

    # Optional: write to CSV
    # os.makedirs("data", exist_ok=True)
    # setlists_clean.to_csv("data/setlists_clean.csv", index=False, encoding="utf-8")
    # albums_clean.to_csv("data/albums_clean.csv", index=False, encoding="utf-8")
    # concert_clean.to_csv("data/concert_clean.csv", index=False, encoding="utf-8")
