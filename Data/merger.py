from functools import reduce
from os import path
from pandas import merge, DataFrame, read_parquet

from .cleaner import (load_clean_dxy, load_clean_fed_funds,
                      load_clean_bitcoin, load_clean_fear_greed)
from .io import save_clean_parquet, dir_path


def get_data() -> DataFrame:
    """
    Returns a DataFrame containing all the necessary data for the model.

    :returns: The merged DataFrame of all other DataFrames.
    """
    cl_path: str = path.join(dir_path, "clean.parquet")

    # If we have already cleaned the file, then return it.
    if path.exists(cl_path):
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
            load_clean_fed_funds()
        )
    )

    # Save the cleaned parquet
    save_clean_parquet(df)

    return df
