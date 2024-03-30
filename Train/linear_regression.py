from joblib import dump, load as jload
from matplotlib import pyplot as plt
from os import path
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from Data import get_split_data

# Directory path
dir_path: str = path.dirname(path.realpath(__file__))


def scale(df: DataFrame, scaler: StandardScaler = None) -> DataFrame:
    """
    Scales the given data set to make it suitable for use in prediction.

    :param df: DataFrame to scale.
    :param scaler: Custom standard scaler to use.
    :returns: the scaled DataFrame.
    """

    if scaler is None:
        scaler = StandardScaler().set_output(transform="pandas")

    return scaler.transform(df)


def simple_train(x_test: DataFrame, x_train: DataFrame, y_train: DataFrame) -> tuple[LinearRegression, DataFrame]:
    """
    :param x_test: X testing data frame.
    :param x_train: X training data frame.
    :param y_train: Y training data frame.
    :returns: The model with the predicted dataframe.
    """
    # Scale the numeric features (all the features in our case)
    scaler: StandardScaler = StandardScaler().set_output(transform="pandas")

    x_train = scaler.fit_transform(x_train)
    x_test = scale(x_test, scaler)

    # LR model
    regressor: LinearRegression = LinearRegression()
    regressor.fit(x_train, y_train)

    return regressor, DataFrame(regressor.predict(x_test), columns=["high", "low", "close"])


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
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        _, y_pred = simple_train(X_test, X_train, y_train)

        res.append(r2_score(y_test, y_pred))

    return res


def train(plot: bool = False) -> (LinearRegression, float):
    """
    :param plot: If true, y_pred and y_test are plotted.
    :returns: The trained model along with its R2 score.
    """
    X, y = get_split_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    regressor, y_pred = simple_train(X_test, X_train, y_train)

    # Evaluate the model
    dump(regressor, path.join(dir_path, "lr_model.sav"))

    if plot:
        plt.plot(X_test.index, y_test['close'], color='r')
        plt.plot(X_test.index, y_pred['close'], color='g')
        plt.show()

    return regressor, r2_score(y_test, y_pred)


def load() -> LinearRegression:
    """
    :returns: The loaded model.
    """
    return jload(path.join(dir_path, "lr_model.sav"))
