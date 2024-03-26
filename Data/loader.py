from dataclasses import asdict
from json import dumps
from opendatasets import download
from os import path, rename, remove
from pandas import DataFrame, read_csv

from Config import config
from Utils import read_json


def load_croissant(dir_name: str) -> DataFrame:
    """
    Loads the data from the given directory using its metadata.json file.
    If not present locally, the dataset is downloaded.
    """

    # Path to the Data file
    dest_path: str = path.join(path.dirname(path.realpath(__file__)), dir_name)
    metadata_path: str = path.join(path.dirname(path.realpath(__file__)), dir_name, "metadata.json")
    meta_data: dict = read_json(metadata_path)
    encoding: str = meta_data['distribution'][1]['encodingFormat'].split('/')[-1]

    # If we have already downloaded the file, then return it.
    if path.exists(path.join(dest_path, f"data.{encoding}")):
        return read_csv(path.join(dest_path, f"data.{encoding}"))

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
    """
    return load_croissant("bitcoin")


def load_dxy() -> DataFrame:
    """
    Loads the DXY (US Dollar Index) data from 2017 to 2023 and returns it as a DataFrame.
    If not present locally, the data must be downloaded manually and placed in the dxy folder.
    Use the following link: https://www.wsj.com/market-data/quotes/index/DXY/historical-prices/download?MOD_VIEW=page&num_rows=2555&range_days=2555&startDate=01/01/2017&endDate=12/31/2023
    """

    # Return the file
    return read_csv(path.join(path.dirname(path.realpath(__file__)), "dxy", "data.csv"))


def load_fed_funds() -> DataFrame:
    """
    Loads the US federal funding rate from 1954 to 2024 and returns it as a DataFrame.
    """

    # Return the file
    return read_csv(path.join(path.dirname(path.realpath(__file__)), "fedFunds", "data.csv"))


def load_inflation() -> DataFrame:
    """
    Loads the US inflation rate from 1954 to 2024 and returns it as a DataFrame.
    """

    # Return the file
    return read_csv(path.join(path.dirname(path.realpath(__file__)), "inflation", "data.csv"))
