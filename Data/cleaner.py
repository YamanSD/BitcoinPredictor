from pandas import DataFrame, Series, Timedelta, to_datetime, read_parquet
from pandas.core.dtypes.common import is_numeric_dtype

from .io import *


def clean_bitcoin() -> tuple[DataFrame, dict]:
    """
    Cleans the Bitcoin dataset and saves it.
    :returns: the cleaned DataFrame along with cleaning statistics.
    """
    df: DataFrame = load_bitcoin()
    stats: dict = {}

    # Initial data size
    init_size: int = len(df.index)

    stats['init_size'] = init_size
    stats['init_shape'] = df.shape

    # Timestamp column name
    ts: str = 'timestamp'

    # Clean the data
    stats['missing_vals'] = df.isna().sum()

    # Remove negative values
    has_neg: bool = False

    for column in df.columns:
        if not is_numeric_dtype(df[column]):
            continue

        if any(df[column] < 0):
            has_neg = True
            df = df[df[column] >= 0]

    stats['has_invalid'] = has_neg

    # Convert string timestamps to DateTime
    df[ts] = to_datetime(df[ts])

    prev_sz: int = len(df.index)

    # Remove duplicated timestamps
    df = df.drop_duplicates(ts, keep="last")

    # Number of duplicates
    dup_sz: int = prev_sz - len(df.index)

    stats['dup_timestamps'] = dup_sz

    # Sort the entries by their timestamp
    df.sort_values(ts, ascending=True, inplace=True)

    ts_diff: Series | DataFrame = df[ts].diff()
    invalid_ts: int = (ts_diff != Timedelta(minutes=1)).sum()

    stats['invalid_timestmaps'] = invalid_ts
    stats['max_timestamp_dif'] = ts_diff.max()
    stats['bad_perc'] = ((invalid_ts + dup_sz) / init_size) * 100

    save_clean_parquet(
        df,
        "bitcoin"
    )

    return df, stats


def clean_dxy() -> DataFrame:
    """
    Cleans the DXY dataset and saves it.
    :returns: the cleaned DataFrame.
    """

    # Timestamp column name
    ts: str = 'Date'

    df: DataFrame = load_dxy()

    # Complete the year
    df[ts] = df[ts].map(lambda d: f"{d[:-2]}20{d[-2:]}")

    # Convert the timestamp column to a datetime object
    df[ts] = to_datetime(df[ts], format="%m/%d/%Y")

    # Set the timestamp column as the index (for df.resample to work)
    df.set_index(ts, inplace=True)

    # Resample the DataFrame into minute intervals and forward fill the values
    df = df.resample('min').ffill()

    # Reset the index
    df.reset_index(inplace=True)

    # Save file
    save_clean_parquet(df, 'dxy')

    return df


def clean_fedFunds() -> DataFrame:
    """
    Cleans the federal funds dataset and saves it.
    :returns: the cleaned DataFrame.
    """

    # Timestamp column name
    ts: str = 'date'

    df: DataFrame = load_fed_funds()

    # Extract only useful dates
    df = df[('2017-01-01' <= df[ts]) & (df[ts] <= '2023-31-12')]

    # Convert the timestamp column to a datetime object
    df[ts] = to_datetime(df[ts], format="%Y-%m-%d")

    # Set the timestamp column as the index (for df.resample to work)
    df.set_index(ts, inplace=True)

    # Resample the DataFrame into minute intervals and forward fill the values
    df = df.resample('min').ffill()

    # Reset the index
    df.reset_index(inplace=True)

    # Save file
    save_clean_parquet(df, 'fedFunds')
    save_clean_csv(df, 'fedFunds')

    return df


def load_clean_fedFunds() -> DataFrame:
    """
    Loads the cleaned US federal funding rate from 2017 to 2023 and returns it as a DataFrame.
    """
    cl_path: str = path.join(dir_path, "fedFunds", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_fedFunds()


def load_clean_dxy() -> DataFrame:
    """
    Loads the cleaned DXY (US Dollar Index) data from 2017 to 2023 and returns it as a DataFrame.
    If not present locally, the data must be downloaded manually and placed in the dxy folder.
    """
    cl_path: str = path.join(dir_path, "dxy", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_dxy()


def load_clean_bitcoin() -> DataFrame:
    """
    Loads the clean bitcoin price Data from 2017 to 2023 and returns it as a DataFrame.
    If not present, the data is cleaned.
    """
    cl_path: str = path.join(dir_path, "bitcoin", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_bitcoin()[0]
