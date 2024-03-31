from joblib import dump, load as jload
from os import path
from sklearn.pipeline import Pipeline


# Directory path
dir_path: str = path.dirname(path.realpath(__file__))


def load(file_name: str) -> Pipeline:
    """

    Args:
        file_name: Name of the file to load, without the sav extension.

    Returns:
        The loaded model from the designated file.

    """
    return jload(path.join(dir_path, f"{file_name}.sav"))


def save(model: Pipeline, file_name: str) -> None:
    """

    Args:
        model: Model to save.
        file_name: Name of the file to save the model in, without the sav extension.

    """
