from numpy import ravel, ndarray
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss  # Check for other testing methods
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from Data import get_data, target_labels

from .common import load as g_load, save as g_save


# Name of the model file, without extension
save_file: str = "lgr_model"


def get_split_data() -> tuple[DataFrame, ndarray]:
    """

    Returns:
        Overrides the usual split, due to the single-dependent-variable nature of LogisticRegression.

    """
    df: DataFrame = get_data()

    return (
        df.drop(target_labels, axis=1),
        ravel(
            (df['open'] - df['close']).map(lambda v: int(v < 0))
        )
    )


def simple_train(
        x_test: DataFrame,
        x_train: DataFrame,
        y_train: DataFrame,
        verbose: bool = False
) -> tuple[Pipeline, DataFrame]:
    """

    Args:
        x_test: X_test dataset.
        x_train: X_train dataset.
        y_train: Y_train dataset.
        verbose: True to make the training verbose.

    Returns:
        The model pipline along with the predicted dataframe.

    """

    # Scale the numeric features (all the features in our case), and then pass to model
    pipeline: Pipeline = Pipeline([
        ('scaler', StandardScaler().set_output(transform="pandas")),
        ('model', LogisticRegression(
            max_iter=400,
            verbose=3 if verbose else 0,
            solver='saga',
            n_jobs=-1,
            penalty='l2',
        ))
    ])

    # LQR model
    pipeline.fit(x_train, y_train)

    return pipeline, DataFrame(pipeline.predict(x_test), columns=["direction"])


def test(n: int) -> list[float]:
    """

    Args:
        n: Number of K-Folds to perform.

    Returns:
        List of accuracy scores for each iteration.

    """

    X, y = get_split_data()
    res: list[float] = []

    # Assuming your data is in X and y
    tscv = TimeSeriesSplit(n_splits=n)  # Use the number of splits you prefer

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y[train_index], y[test_index]

        _, y_pred = simple_train(X_test, X_train, y_train)

        res.append(brier_score_loss(y_test, y_pred))

    return res


def train(no_save: bool = False, verbose: bool = False) -> tuple[Pipeline, float]:
    """

    Trains the model and saves it to its designated file.

    Args:
        no_save: True to not save the trained model.
        verbose: True to make the training step verbose.

    Returns:
        The trained model along with its brier score loss value.

    """
    X, y = get_split_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    pipeline, y_pred = simple_train(X_test, X_train, y_train, verbose)

    # Evaluate the model
    if not no_save:
        save(pipeline)

    return pipeline, brier_score_loss(y_test, y_pred)


def load() -> Pipeline:
    """

    Returns:
        The loaded model from the designated file.

    """
    return g_load(save_file)


def save(model: Pipeline) -> None:
    """

    Saves the model into its file.

    Args:
        model: Model to be saved into the file.


    """
    g_save(model, save_file)
