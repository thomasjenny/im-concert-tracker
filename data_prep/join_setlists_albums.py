import pandas as pd


def join_setlists_albums(
    setlists_df: pd.DataFrame, albums_df: pd.DataFrame
) -> pd.DataFrame:
    """Performs a join of the setlists and album tables to enrich the
    setlists data with the corresponding albums to the songs

    Args:
        setlists_df (DataFrame): cleaned version of the setlist.fm
            setlists data
        albums_df (DataFrame): cleaned version of the musicbrainz
            albums data

    Returns:
        concerts (DataFrame): the setlists data with an additional
            albums column
    """
    concerts = pd.merge(
        setlists_df, albums_df, left_on="song_title", right_on="song_name", how="left"
    )

    concerts = concerts.drop(columns=["song_position", "song_name"])
    return concerts


if __name__ == "__main__":
    import os
    from pathlib import Path

    in_path = Path(Path.cwd() / "data_prep" / "data" / "csv")

    # Load setlists data
    setlists_file = "setlists_clean.csv"
    setlists = pd.read_csv(Path(in_path / setlists_file))
    albums_file = "albums_clean.csv"
    albums = pd.read_csv(Path(in_path / albums_file))

    # Run the join function
    concerts = join_setlists_albums(setlists, albums)

    # Save the clean data to CSV
    out_path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    os.makedirs(out_path, exist_ok=True)
    concerts.to_csv(Path(out_path / "concerts_clean.csv"), index=False)
