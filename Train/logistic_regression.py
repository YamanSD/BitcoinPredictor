from joblib import dump, load as jload
from matplotlib import pyplot as plt
from os import path

from numpy import ravel, ndarray
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score  # Check for other testing methods
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from Data import get_data

# Directory path
dir_path: str = path.dirname(path.realpath(__file__))


def get_split_data() -> tuple[DataFrame, ndarray]:
    """
    :returns: Properly split data for logistic regression
    """
    df: DataFrame = get_data()

    return (
        df.drop(['close', 'high', 'low'], axis=1),
        ravel(
            (df['open'] - df['close']).map(lambda v: -1 if v < 0 else int(0 < v))
        )
    )


def simple_train(x_test: DataFrame, x_train: DataFrame, y_train: DataFrame) -> tuple[LogisticRegression, DataFrame]:
    """
    :param x_test: X testing data frame.
    :param x_train: X training data frame.
    :param y_train: Y training data frame.
    :returns: The model with the predicted dataframe.
    """
    # Scale the numeric features (all the features in our case)
    scaler: StandardScaler = StandardScaler().set_output(transform="pandas")

    x_train = scaler.fit_transform(x_train)
    x_test = scaler.transform(x_test)

    # LR model
    regressor: LogisticRegression = LogisticRegression(max_iter=400)
    regressor.fit(x_train, y_train)

    return regressor, DataFrame(regressor.predict(x_test), columns=["direction"])


def test(n: int) -> list[float]:
    """
    Tests the simple_train function on k-cross validation.

    :param n: Number of iterations.
    :return: A list of R2 scores for each iteration.
    """
    X, y = get_split_data()
    res: list[float] = []

    # Assuming your data is in X and y
    tscv = TimeSeriesSplit(n_splits=n)  # Use the number of splits you prefer

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y[train_index], y[test_index]

        _, y_pred = simple_train(X_test, X_train, y_train)

        res.append(accuracy_score(y_test, y_pred))

    return res


def train(plot: bool = False) -> (LogisticRegression, float):
    """
    :param plot: If true, y_pred and y_test are plotted.
    :returns: The trained model along with its R2 score.
    """
    X, y = get_split_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    regressor, y_pred = simple_train(X_test, X_train, y_train)

    # Evaluate the model
    dump(regressor, path.join(dir_path, "lgr_model.sav"))

    if plot:
        plt.plot(X_test.index, y_test['direction'], color='r')
        plt.plot(X_test.index, y_pred['direction'], color='g')
        plt.show()

    return regressor, accuracy_score(y_test, y_pred)


def load() -> LogisticRegression:
    """
    :returns: The loaded model.
    """
    return jload(path.join(dir_path, "lgr_model.sav"))
