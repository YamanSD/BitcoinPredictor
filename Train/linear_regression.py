from joblib import dump, load as jload
from os import path
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from Data import get_split_data


# Directory path
dir_path: str = path.dirname(path.realpath(__file__))


def train() -> (LinearRegression, float):
    X, y = get_split_data()

    # Plot correlation
    # c = x.corr()
    # c.columns = x.columns
    #
    # sns.heatmap(c, annot=True, cmap='coolwarm', fmt=".2f")
    #
    # plt.show()

    # Create a dictionary containing potential values of alpha
    # alpha_values: dict = {
    #     'alpha': [0.00005, 0.0005, 0.001, 0.01, 0.05, 0.06, 0.08, 1, 2, 3, 5, 8, 10, 20, 50, 100],
    #     'l1_ratio': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1]
    # }
    #
    # elastic: GridSearchCV = GridSearchCV(
    #     ElasticNet(),
    #     alpha_values,
    #     scoring='neg_mean_squared_error',
    #     cv=10
    # )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    # Scale the numeric features (all the features in our case)
    scaler: StandardScaler = StandardScaler().set_output(transform="pandas")

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # elastic.fit(X_train, y_train)
    # y_pred: DataFrame = elastic.predict(X_test)

    # Evaluate the model
    # r2: float = r2_score(y_test, y_pred)
    #
    # print("R2 Elastic: ", r2)

    # LR model
    regressor: LinearRegression = LinearRegression()

    regressor.fit(X_train, y_train)
    y_pred: DataFrame = DataFrame(regressor.predict(X_test), columns=["high", "low", "close"])

    # Evaluate the model
    dump(regressor, path.join(dir_path, "model.sav"))

    print(X_train.iloc[0])

    return regressor, r2_score(y_test, y_pred)


def load() -> LinearRegression:
    """
    :returns: The loaded model.
    """
    return jload(path.join(dir_path, "model.sav"))
