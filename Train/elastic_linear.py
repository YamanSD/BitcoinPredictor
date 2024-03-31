from pandas import DataFrame
from sklearn.experimental import enable_halving_search_cv  # noqa To use HalvingGridSearchCV
from sklearn.linear_model import ElasticNet
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, TimeSeriesSplit, HalvingGridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from Data import get_split_data

from .common import load as g_load, save as g_save


# Name of the model file, without extension
save_file: str = "elr_model"


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

    # Create a dictionary containing potential values of alpha and l1
    alpha_values: dict = {
        'alpha': [0.00005, 0.0005, 0.001, 0.01, 0.05, 0.06, 0.08, 1, 2, 3, 5, 8, 10, 20, 50, 100],
        'l1_ratio': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1]
    }

    # Scale the numeric features (all the features in our case), and then pass to model
    pipeline: Pipeline = Pipeline([
        ('scaler', StandardScaler().set_output(transform="pandas")),
        (
            'model',
            HalvingGridSearchCV(
                ElasticNet(),
                alpha_values,
                scoring='neg_mean_squared_error',
                cv=10,
                verbose=3 if verbose else 0
            )
        )
    ])

    # Check https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.HalvingRandomSearchCV.html
    pipeline.fit(x_train, y_train)

    return pipeline, DataFrame(pipeline.predict(x_test), columns=["high", "low", "close"])


def test(n: int) -> list[int]:
    """

    Args:
        n: Number of K-Folds to perform.

    Returns:
        List of R2 scores for each iteration.

    """

    X, y = get_split_data()
    res: list[int] = []

    # Assuming your data is in X and y
    tscv = TimeSeriesSplit(n_splits=n)  # Use the number of splits you prefer

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        _, y_pred = simple_train(X_test, X_train, y_train)

        res.append(r2_score(y_test, y_pred))

    return res


def train(*, no_save: bool = False, verbose: bool = False) -> tuple[Pipeline, float]:
    """

    Trains the model and saves it to its designated file.

    Args:
        no_save: True to not save the trained model.
        verbose: True to make the training step verbose.

    Returns:
        The trained model along with its R2 score.

    """

    X, y = get_split_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    pipeline, y_pred = simple_train(X_test, X_train, y_train, verbose)

    # Evaluate the model
    if not no_save:
        save(pipeline)

    return pipeline, r2_score(y_test, y_pred)


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
