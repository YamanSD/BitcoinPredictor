import numpy as np

from matplotlib import pyplot as plt
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from Data import get_split_data


# https://towardsdatascience.com/a-step-by-step-introduction-to-pca-c0d78e26a0dd

def standardize() -> np.ndarray:
    """
    :returns: The standardized ndarray for the DataFrame.
    """

    # Standardize the data
    return StandardScaler().fit_transform(get_split_data()[0])


def calc_cov() -> np.ndarray:
    """
    :returns: The covariance matrix.
    """
    x: np.ndarray = standardize()

    return (x.T @ x) / (x.shape[0] - 1)


def eigen_comp(plot: bool = False) -> np.ndarray:
    """
    :param plot: True to plot the sorted eigen compositions.
    :returns: The sorted eigen vector matrix.
    """
    cov: np.ndarray = calc_cov()

    # Eigenvectors and eigenvalues of the covariance matrix
    eig_values, eig_vectors = np.linalg.eig(cov)

    idx: np.ndarray = np.argsort(eig_values, axis=0)[::-1]

    if plot:
        cumsum: np.ndarray = np.cumsum(eig_values[idx]) / np.sum(eig_values[idx])
        xint: range = range(1, len(cumsum) + 1)

        plt.plot(xint, cumsum)

        plt.xlabel("Number of components")
        plt.ylabel("Cumulative explained variance")
        plt.xticks(xint)
        plt.show()

    return eig_vectors[:, idx]


