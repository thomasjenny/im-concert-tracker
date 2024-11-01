import pandas as pd


def join_setlists_albums(
    setlists_df: pd.DataFrame, albums_df: pd.DataFrame
) -> pd.DataFrame:

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

    concerts = join_setlists_albums(setlists, albums)

    # Save the clean data to CSV
    out_path = Path(Path.cwd() / "data_prep" / "data" / "csv")
    os.makedirs(out_path, exist_ok=True)
    concerts.to_csv(Path(out_path / "concerts_test.csv"), index=False)

