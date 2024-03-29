from joblib import dump, load as jload
from matplotlib import pyplot as plt
from os import path
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from Data import get_split_data, get_data

# Directory path
dir_path: str = path.dirname(path.realpath(__file__))


def train() -> (LinearRegression, float):
    X, y = get_split_data()
    df = get_data()

    print(df[['close', 'open']].head(100))
    print(df.columns)
    plt.plot(range(len(X)), df['open'], color='r')
    plt.show()
    plt.plot(range(len(X)), df['close'], color='b')
    plt.show()
    plt.plot(range(len(X)), df['volume'], color='c')
    plt.show()
    plt.plot(range(len(X)), df['quote_asset_volume'], color='m')
    plt.show()
    plt.plot(range(len(X)), df['taker_buy_quote_asset_volume'], color='b')
    plt.show()
    plt.plot(range(len(X)), df['open_dxy'], color='y')
    plt.show()
    plt.plot(range(len(X)), df['fng'], color='olive')
    plt.show()
    plt.plot(range(len(X)), df['fed_rate'], color='seagreen')
    plt.show()
    return

    # FOR TESTING
    # Assuming your data is in X and y
    tscv = TimeSeriesSplit(n_splits=10)  # Use the number of splits you prefer
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        # Scale the numeric features (all the features in our case)
        scaler: StandardScaler = StandardScaler().set_output(transform="pandas")

        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        regressor: LinearRegression = LinearRegression()

        regressor.fit(X_train, y_train)
        y_pred: DataFrame = DataFrame(regressor.predict(X_test), columns=["high", "low", "close"])

        # Evaluate the model
        dump(regressor, path.join(dir_path, "model.sav"))

        print(r2_score(y_test, y_pred))

    return
    # FOR TESTING

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
