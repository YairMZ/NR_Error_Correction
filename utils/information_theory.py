"""various statistical functions, information theory measures, and convenience wrappers around scipy"""
import numpy as np
from scipy.stats import entropy as ent  # type: ignore
from typing import Union
from .custom_exceptions import UnsupportedDtype   # type: ignore


def prob(data: np.ndarray, return_labels: bool = False) -> Union[np.ndarray, tuple[np.ndarray, list]]:
    """Estimate the probability distribution given samples. Doesn't work with floating point values.

    :param data: a 1D or 2D numpy array. Each row is a dimension and each column an observation
    :param return_labels: if true, labels of frequencies are also returned. Tuple is returned instead of array.
    :return: a 2D array of of probabilities. Rows are RV dimension, and columns are alphabet size
    """
    if data.dtype in [float, np.float64]:
        raise UnsupportedDtype()
    # TODO - add ability to return joint distribution - can be done with np.unique along axis

    if data.ndim == 2:
        alphabet: list = (np.unique(data)).tolist()
        alphabet_size = len(alphabet)
        pr = np.zeros((data.shape[0], alphabet_size))
        num_samples = data.shape[1]
        for row_idx, row in enumerate(data):
            values, counts = np.unique(row, return_counts=True)
            for val, count in zip(values, counts):
                pr[row_idx][alphabet.index(val)] = count
        pr = np.divide(pr, num_samples)
        if return_labels:
            return pr, alphabet
        else:
            return pr
        # return np.apply_along_axis(lambda x: np.bincount(x, minlength=alphabet_size), axis=1, arr=data)/num_samples
    elif data.ndim == 1:
        num_samples = data.shape[0]
        alphabet, pr = np.unique(data, return_counts=True)
        pr = np.divide(pr, num_samples)
        if return_labels:
            return pr, alphabet.tolist()
        else:
            return pr
    else:
        raise ValueError("only scalar and vector RV's currently supported (dim=1,2)")


def entropy(pk: np.ndarray, base: int = 2) -> Union[np.ndarray, float]:
    """This is a wrapper around scipy's entropy function. Seamlessly treat 1d and 2d arrays.

    :param pk: an array representing a PMF. number of columns is alphabet size, and number of rows is number of RV's.
    :param base: base of logarithm for entropy calculation. Defaults to 2 (entropy in units of bits).
    """
    if pk.ndim == 2:
        return ent(pk, base=base, axis=1)
    if pk.ndim == 1:
        return ent(pk, base=base)
    raise ValueError("only scalar and vector RV's currently supported (dim=1,2)")
