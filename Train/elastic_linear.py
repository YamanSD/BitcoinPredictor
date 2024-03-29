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
# Check https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.HalvingRandomSearchCV.html
# elastic.fit(X_train, y_train)
# y_pred: DataFrame = elastic.predict(X_test)

# Evaluate the model
# r2: float = r2_score(y_test, y_pred)
#
# print("R2 Elastic: ", r2)
# from joblib import dump, load as jload
# from os import path
# from pandas import DataFrame
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import r2_score
# from sklearn.model_selection import train_test_split, TimeSeriesSplit
# from sklearn.preprocessing import StandardScaler
#
# from Data import get_split_data
#
# # Directory path
# dir_path: str = path.dirname(path.realpath(__file__))
#
#
# def simple_train(x_test: DataFrame, x_train: DataFrame, y_train: DataFrame) -> tuple[LinearRegression, DataFrame]:
#     """
#     :param x_test: X testing data frame.
#     :param x_train: X training data frame.
#     :param y_train: Y training data frame.
#     :returns: The model with the predicted dataframe.
#     """
#     # Scale the numeric features (all the features in our case)
#     scaler: StandardScaler = StandardScaler().set_output(transform="pandas")
#
#     x_train = scaler.fit_transform(x_train)
#     x_test = scaler.transform(x_test)
#
#     # LR model
#     regressor: LinearRegression = LinearRegression()
#     regressor.fit(x_train, y_train)
#
#     return regressor, DataFrame(regressor.predict(x_test), columns=["high", "low", "close"])
#
#
# def test(n: int) -> list[int]:
#     """
#     Tests the simple_train function on k-cross validation.
#
#     :param n: Number of iterations.
#     :return: A list of R2 scores for each iteration.
#     """
#     X, y = get_split_data()
#     res: list[int] = []
#
#     # Assuming your data is in X and y
#     tscv = TimeSeriesSplit(n_splits=n)  # Use the number of splits you prefer
#
#     for train_index, test_index in tscv.split(X):
#         X_train, X_test = X.iloc[train_index], X.iloc[test_index]
#         y_train, y_test = y.iloc[train_index], y.iloc[test_index]
#
#         _, y_pred = simple_train(X_test, X_train, y_train)
#
#         res.append(r2_score(y_test, y_pred))
#
#     return res
#
#
# def train() -> (LinearRegression, float):
#     X, y = get_split_data()
#
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)
#
#     regressor, y_pred = simple_train(X_test, X_train, y_train)
#
#     # Evaluate the model
#     dump(regressor, path.join(dir_path, "lr_model.sav"))
#
#     return regressor, r2_score(y_test, y_pred)
#
#
# def load() -> LinearRegression:
#     """
#     :returns: The loaded model.
#     """
#     return jload(path.join(dir_path, "lr_model.sav"))
