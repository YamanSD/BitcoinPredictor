from dataclasses import asdict
from json import dumps
from opendatasets import download
from os import path, rename, remove, mkdir
from pandas import DataFrame, read_csv
from requests import get
from typing import Literal

from Config import config
from Utils import read_json


# Directory path
dir_path: str = path.dirname(path.realpath(__file__))


def load_croissant(dir_name: str) -> DataFrame:
    """

    If not present locally, the dataset is downloaded.

    Args:
        dir_name: Directory of the CroissantML metadata.json file to load.

    Returns:
        The loaded DataFrame.

    """

    # Path to the Data file
    dest_path: str = path.join(dir_path, dir_name)
    metadata_path: str = path.join(dir_path, dir_name, "metadata.json")
    meta_data: dict = read_json(metadata_path)
    encoding: str = meta_data['distribution'][1]['encodingFormat'].split('/')[-1]
    cl_path: str = path.join(dest_path, f"data.{encoding}")

    # If we have already downloaded the file, then return it.
    if path.exists(cl_path):
        return read_csv(cl_path)

    url: str = meta_data['url']
    folder_name: str = url.split('/')[-1]
    file_name: str = meta_data['distribution'][1]['name']

    # Create the kaggle.json config. Needed here due to implementation of opendatasets
    with open('./kaggle.json', 'w') as file:
        file.write(dumps(asdict(config.kaggle)))

    # Download the file
    download(url, data_dir=dest_path)

    rename(
        path.join(dest_path, folder_name, file_name),
        path.join(dest_path, f"data.{encoding}")
    )

    # Remove the downloaded folder
    remove(path.join(dest_path, folder_name))

    # Return re-read the file
    return load_croissant(dir_name)


def load_bitcoin() -> DataFrame:
    """
    Loads the bitcoin price Data from 2017 to 2023 and returns it as a DataFrame.
    If not present locally, the dataset is downloaded.

    Returns:
        DataFrame containing the training BTC data.

    """
    return load_croissant("bitcoin")


def load_dxy() -> DataFrame:
    """
    Loads the DXY (US Dollar Index) data from 2017 to 2023 and returns it as a DataFrame.
    If not present locally, the data must be downloaded manually and placed in the dxy folder.

    Returns:
        DataFrame containing the training DXY data.

    """
    return read_csv(path.join(dir_path, "dxy", "data.csv"))


def load_fear_greed() -> DataFrame:
    """
    Loads the Fear and Greed data from 2018 to 2024 and returns it as a DataFrame.
    If not present locally, the data is downloaded from the URL in the config file.

    Returns:
        DataFrame containing the training FNG data.

    """
    dir_name: str = "fearGreed"

    # Path to the Data file
    dest_path: str = path.join(dir_path, dir_name)
    cl_path: str = path.join(dest_path, f"data.csv")

    # If we have already downloaded the file, then return it.
    if path.exists(cl_path):
        return read_csv(cl_path)

    # Create the missing dir
    mkdir(dest_path)

    # Extract the JSON data
    res: dict = get(
        config.fng.historical_url,
        proxies=config.proxies
    ).json()["data"]

    df: DataFrame = DataFrame.from_dict(res)

    # Drop the useless column
    df.drop("time_until_update", axis=1, inplace=True)

    # Save the data to a CSV
    df.to_csv(cl_path)

    return df


def load_fed_funds() -> DataFrame:
    """
    Loads the US federal funding rate from 1954 to 2024 and returns it as a DataFrame.

    Returns:
        DataFrame containing the training FederalRate data.

    """
    return read_csv(path.join(dir_path, "fedFunds", "data.csv"))


def save_parquet(
        df: DataFrame,
        folder: Literal['bitcoin', 'dxy', 'fedFunds', 'inflation', 'fearGreed'] = '',
        file_name: str = None
) -> None:
    """
    The DataFrame is saved in the appropriate location as a parquet file.

    Args:
        df: DataFrame to save.
        folder: Folder to save the file in. From a list of predefined folders.
        file_name: File name to save the data in, no extension. Default is clean.

    """
    df.to_parquet(path.join(dir_path, folder, f"{file_name if file_name else 'clean'}.parquet"))
