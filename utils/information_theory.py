"""various statistical functions, information theory measures, and convenience wrappers around scipy"""
import numpy as np
from scipy.stats import entropy as scipy_ent  # type: ignore
from typing import Union
from .custom_exceptions import UnsupportedDtype


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
        pr: np.ndarray = np.zeros((data.shape[0], alphabet_size))
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
    elif data.ndim == 1:
        num_samples = data.shape[0]
        alphabet_arr, pr = np.unique(data, return_counts=True)
        pr = np.divide(pr, num_samples)
        if return_labels:
            return pr, alphabet_arr.tolist()
        else:
            return pr
    else:
        raise ValueError("only scalar and vector RV's currently supported (dim=1,2)")


def entropy(pk: np.ndarray, base: int = 2) -> Union[np.ndarray, float]:
    """This is a wrapper around scipy's entropy function. Seamlessly treat 1d and 2d arrays.

    :param pk: an array representing a PMF. number of columns is alphabet size, and number of rows is number of RV's.
    :param base: base of logarithm for entropy calculation. Defaults to 2 (entropy in units of bits).
    :rtype: Union[np.ndarray, float]
    """
    if pk.ndim == 2:
        return scipy_ent(pk, base=base, axis=1)
    if pk.ndim == 1:
        return scipy_ent(pk, base=base)
    raise ValueError("only scalar and vector RV's currently supported (dim=1,2)")


def typical_set_cardinality(n: int, pk: np.ndarray = None, ent: float = None, eps: float = 1e-5) -> tuple[float, float]:
    # noinspection LongLine
    """Given an distribution describing an i.i.d process, how many typical sequences of length n are there?

    The cardinality of a typical set is dictated by the AEP. See:
    https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-441-information-theory-spring-2010/lecture-notes/MIT6_441S10_lec03.pdf
    :param n: The length of the sequence
    :param pk: Defaults to None. If specified, a 1d array representing a PMF of a univariate RV.
    :param ent: The entropy of the variable. Defaults to None, in which case it is inferred from distribution. If specified, it is used and pk is ignored
    :param eps: The epsilon used for the calculation
    :return: An tuple representing a lower and  upper bounds on the cardinality of the typical set of sequences of length n.
    """
    if n <= 0 or eps <= 0:
        raise ValueError()
    if ent is None:
        if pk is None:
            raise ValueError()
        else:
            ent_f = entropy(pk, base=2)
    else:
        ent_f = ent
    if not isinstance(ent_f, (float, int)):
        raise ValueError()
    ub = 2**(n * (ent_f + eps))
    lb = (1 - eps) * 2**(n * (ent_f - eps))
    return lb, ub
