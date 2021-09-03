"""various statistical functions, information theory measures, and convenience wrappers around scipy"""
import numpy as np
from scipy.stats import entropy as ent  # type: ignore
from typing import Union


def prob(data: np.ndarray, alphabet_size=None) -> np.ndarray:
    """Estimate the probability distribution given samples

    :param data: a 1D or 2D numpy array. Each row is a dimension and each column an observation
    :param alphabet_size: If left as None, inferred from data.
    :return: a 2D array of of probabilities. Rows are RV dimension, and columns are alphabet size
    """
    # TODO - add ability to return joint distribution
    if alphabet_size is None:
        alphabet_size = len(np.unique(data))
    if data.ndim == 2:
        num_samples = data.shape[1]
        return np.apply_along_axis(lambda x: np.bincount(x, minlength=alphabet_size), axis=1, arr=data)/num_samples
    if data.ndim == 1:
        num_samples = data.shape[0]
        return np.bincount(data, minlength=alphabet_size)/num_samples
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
