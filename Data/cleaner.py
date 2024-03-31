from os import path
from pandas import DataFrame, Series, Timedelta, to_datetime, \
    read_parquet, concat, Timestamp, to_numeric
from pandas.core.dtypes.common import is_numeric_dtype

from .io import load_fed_funds, load_bitcoin, load_dxy, \
    save_parquet, dir_path, load_fear_greed


def clean_bitcoin() -> tuple[DataFrame, dict]:
    """

    Cleans the Bitcoin dataset and saves it.

    Returns:
        DataFrame containing the cleaned BTC data.

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

    stats['invalid_timestamps'] = invalid_ts
    stats['max_timestamp_dif'] = ts_diff.max()
    stats['bad_perc'] = ((invalid_ts + dup_sz) / init_size) * 100

    # Set the timestamp column as the index
    df.set_index(ts, inplace=True)

    save_parquet(
        df,
        "bitcoin"
    )

    return df, stats


def clean_dxy() -> DataFrame:
    """

    Cleans the DXY dataset and saves it.

    Returns:
        DataFrame containing the cleaned DXY data.

    """

    # Timestamp column name
    ts: str = 'timestamp'

    df: DataFrame = load_dxy()

    # Rename the columns
    df.rename(columns={
        " Open": "open_dxy",
        "Date": "timestamp"
    }, inplace=True)

    # Drop irrlevant columns
    df.drop([" High", " Low", " Close"], inplace=True, axis=1)

    # Complete the year
    df[ts] = df[ts].map(lambda d: f"{d[:-2]}20{d[-2:]}")

    # Convert the timestamp column to a datetime object
    df[ts] = to_datetime(df[ts], format="%m/%d/%Y")

    # Set the timestamp column as the index (for df.resample to work)
    df.set_index(ts, inplace=True)

    # Resample the DataFrame into minute intervals and forward fill the values
    df = df.resample('min').ffill()

    # Save file
    save_parquet(df, 'dxy')

    return df


def clean_fed_funds() -> DataFrame:
    """

    Cleans the federal funds dataset and saves it.

    Returns:
        DataFrame containing the cleaned FedRate data.

    """

    # Timestamp column name
    ts: str = 'timestamp'

    df: DataFrame = load_fed_funds()

    # Rename the columns
    df.rename(columns={
        " value": "fed_rate",
        "date": "timestamp"
    }, inplace=True)

    # Convert the timestamp column to a datetime object
    df[ts] = to_datetime(df[ts], format="%Y-%m-%d")

    # Extract only useful dates
    df = df[(Timestamp('2017-01-01') <= df[ts]) & (df[ts] <= Timestamp('2023-12-31'))]

    # Set the timestamp column as the index (for df.resample to work)
    df.set_index(ts, inplace=True)

    # Resample the DataFrame into minute intervals and forward fill the values
    df = df.resample('min').ffill()

    # Save file
    save_parquet(df, 'fedFunds')

    return df


def clean_fear_greed() -> DataFrame:
    """

    Cleans the fear and greed dataset and saves it.

    Returns:
        DataFrame containing the cleaned FNG data.

    """

    # Timestamp column name
    ts: str = 'timestamp'

    df: DataFrame = load_fear_greed()

    # Drop any unnamed columns
    df.drop((c for c in df.columns if "Unnamed" in c), axis=1, inplace=True)

    # Rename the columns
    df.rename(columns={
        "value": "fng",
    }, inplace=True)

    # Drop the classification string
    df.drop("value_classification", axis=1, inplace=True)

    # This fng value is based on the bitcoin upward trend in 2017
    missing_df: DataFrame = DataFrame.from_dict({ts: ['01-01-2017'], 'fng': [70]})

    # Join the missing value with the current values
    df = concat([missing_df, df]).reset_index(drop=True)

    # Convert the timestamp column to a datetime object
    df[ts] = to_datetime(df[ts], format="%d-%m-%Y")

    # Extract only useful dates
    df = df[(Timestamp('2017-01-01') <= df[ts]) & (df[ts] <= Timestamp('2023-12-31'))]

    # Convert index from str to numeric
    df['fng'] = to_numeric(df['fng'])

    # Set the timestamp column as the index (for df.resample to work)
    df.set_index(ts, inplace=True)

    # Resample the DataFrame into minute intervals and forward fill the values
    df = df.resample('min').ffill()

    # Save file
    save_parquet(df, 'fearGreed')

    return df


def load_clean_fear_greed() -> DataFrame:
    """

    Loads the cleaned fear and greed index from 2017 to 2023 and returns it as a DataFrame.

    Returns:
        DataFrame containing the cleaned FNG data.

    """
    cl_path: str = path.join(dir_path, "fearGreed", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_fear_greed()


def load_clean_fed_funds() -> DataFrame:
    """

    Loads the cleaned US federal funding rate from 2017 to 2023 and returns it as a DataFrame.

    Returns:
        DataFrame containing the cleaned FedRate data.

    """
    cl_path: str = path.join(dir_path, "fedFunds", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_fed_funds()


def load_clean_dxy() -> DataFrame:
    """

    Loads the cleaned DXY (US Dollar Index) data from 2017 to 2023 and returns it as a DataFrame.
    If not present locally, the data must be downloaded manually and placed in the dxy folder.

    Returns:
        DataFrame containing the cleaned DXY data.

    """
    cl_path: str = path.join(dir_path, "dxy", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_dxy()


def load_clean_bitcoin() -> DataFrame:
    """

    Loads the clean bitcoin price Data from 2017 to 2023 and returns it as a DataFrame.
    If not present, the data is downloaded and cleaned.

    Returns:
        DataFrame containing the cleaned BTC data.

    """
    cl_path: str = path.join(dir_path, "bitcoin", "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
        return read_parquet(cl_path)

    return clean_bitcoin()[0]
