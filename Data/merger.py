from functools import reduce
from pandas import merge

from .cleaner import *
from .io import save_parquet, dir_path


# List of target labels
target_labels: list[str] = ['close', 'high', 'low']


def get_data(refresh: bool = False) -> DataFrame:
    """

    Args:
        refresh: If True, re-cleans the datasets.

    Returns:
        The merged DataFrame of all other DataFrames.
        Suitable for use in training.

    """
    cl_path: str = path.join(dir_path, "clean.parquet")

    # If we have already cleaned the file, then return it.
    if not refresh and path.exists(cl_path):
        return read_parquet(cl_path)

    df: DataFrame = reduce(
        lambda left, right: merge(
            left,
            right,
            how='left',
            left_index=True,
            right_index=True
        ),
        (
            load_clean_bitcoin(),
            load_clean_dxy(),
            load_clean_fear_greed(),
            load_clean_fed_funds(),
            load_clean_sentiment()
        ) if not refresh else (
            clean_bitcoin()[0],
            clean_dxy(),
            clean_fear_greed(),
            clean_fed_funds(),
            clean_sentiment()
        )
    )

    # Remove invalid rows
    df.dropna(inplace=True)

    # Save the cleaned parquet
    save_parquet(df)

    return df


def get_split_data(refresh: bool = False) -> tuple[DataFrame, DataFrame]:
    """

    Args:
        refresh: If True, recleans the datasets.

    Returns:
        The merged DataFrame split into X and Y DataFrames.

    """
    global target_labels

    df: DataFrame = get_data(refresh)

    return df.drop(target_labels, axis=1), df[target_labels]
