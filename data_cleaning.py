import pandas as pd


def clean_albums_table(albums_table):
    """Change some song names in the albums table that differ from the
    setlists table (different capitalization or apostrophes).

    Args:
        albums_table (dataframe): the albums table

    Returns:
        albums_table_clean (dataframe): the cleaned albums table
    """
    # Harmonize song names
    replacement_mapping_dict = {
        "Blood on the World’s Hands": "Blood on the World's Hands",
        "Bring Your Daughter… to the Slaughter": "Bring Your Daughter... to the Slaughter",
        "Children Of The Damned": "Children of the Damned",
        "Run To The Hills": "Run to the Hills",
        "The Number Of The Beast": "The Number of the Beast",
    }
    albums_table.replace(replacement_mapping_dict, inplace=True)

    # Add "Total Eclipse" and the corresponding album
    new_row = pd.Series(
        {"album_name": "The Number of the Beast", "song_name": "Total Eclipse"},
    )
    albums_table = pd.concat([albums_table, new_row.to_frame().T], ignore_index=True)

    return albums_table


def clean_setlists_table(setlists_table):
    """Change some song names in the albums table that differ from the
    setlists table (different capitalization or apostrophes).

    Args:
        albums_table (dataframe): the albums table

    Returns:
        albums_table_clean (dataframe): the cleaned albums table
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
    setlists_table.replace(replacement_mapping_dict, inplace=True)

    return setlists_table


if __name__ == "__main__":
    albums = pd.read_csv("data/albums.csv")
    setlists = pd.read_csv("data/setlist.csv")

    def filter_non_album_songs(setlists_df, albums_df):
        """Helper function to filter unique song names that are in the
        "setlists" table, but not in the "albums" table
        """
        filter = setlists_df[~setlists_df["song_name"].isin(albums_df["song_name"])]
        filter = filter.drop_duplicates(subset="song_name")
        return filter

    # Test if studio album songs have been renamed in the "albums" table
    # to reflect the "setlists" table
    albums_clean = clean_albums_table(albums)
    filter_albums_before = filter_non_album_songs(setlists, albums)
    filter_albums_after = filter_non_album_songs(setlists, albums_clean)

    # Test if duplicates in the "setlists" table of non-Maiden songs
    # have been renamed correctly
    setlists_clean = clean_setlists_table(setlists)
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
