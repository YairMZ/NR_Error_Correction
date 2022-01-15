"""various statistical functions, information theory measures, and convenience wrappers around scipy"""
import numpy as np
from scipy.stats import entropy as scipy_ent
from typing import Any, Optional
from utils.custom_exceptions import UnsupportedDtype
import numpy.typing as npt


def prob_with_alphabet(data: npt.NDArray[Any]) -> tuple[npt.NDArray[np.float_], list[Any]]:
    """Estimate the probability distribution given samples. Doesn't work with floating point values.

    :param data: a 1D or 2D numpy array. Each row is a dimension and each column an observation
    :return: a tuple: prob, alphabet. prob is a 2D array of probabilities. Rows are RV dimension, and columns
    are alphabet size, alphabet is a list with the inferred alphabet.
    """
    if data.dtype in [float, np.dtype(np.float_)]:
        raise UnsupportedDtype()
    # TODO - add ability to return joint distribution - can be done with np.unique along axis

    if data.ndim == 2:
        alphabet: list[Any] = np.unique(data).tolist()
        alphabet_size = len(alphabet)
        pr: npt.NDArray[np.float_] = np.zeros((data.shape[0], alphabet_size))
        num_samples = data.shape[1]
        for row_idx, row in enumerate(data):
            values: npt.NDArray[Any]
            values, counts = np.unique(row, return_counts=True)
            for val, count in zip(values, counts):
                pr[row_idx][alphabet.index(val)] = count
        pr = np.divide(pr, num_samples)
        return pr, alphabet
    elif data.ndim == 1:
        num_samples = data.shape[0]
        alphabet_arr: npt.NDArray[Any]
        alphabet_arr, pr = np.unique(data, return_counts=True)
        pr = np.divide(pr, num_samples)
        return pr, alphabet_arr.tolist()
    else:
        raise ValueError("only scalar and vector RV's currently supported (dim=1,2)")


def prob(data: npt.NDArray[Any]) -> npt.NDArray[np.float_]:
    """A wrapper around prob_with_alphabet which doesn't return the alphabet.

    :param data: a 1D or 2D numpy array. Each row is a dimension and each column an observation
    :return: a 2D array of probabilities. Rows are RV dimension, and columns are alphabet size.
    """
    pr, alphabet = prob_with_alphabet(data)
    return pr


def entropy(pk: npt.NDArray[Any], base: int = 2) -> npt.NDArray[Any]:
    """This is a wrapper around scipy's entropy function. Seamlessly treat 1d and 2d arrays.

    :param pk: an array representing a PMF. number of columns is alphabet size, and number of rows is number of RV's.
    :param base: base of logarithm for entropy calculation. Defaults to 2 (entropy in units of bits).
    :rtype: np.ndarray
    """
    if pk.ndim not in (1, 2):
        raise ValueError("only scalar and vector RV's currently supported (dim=1,2)")
    if pk.ndim == 2:
        ent = scipy_ent(pk, base=base, axis=1)
    else:
        ent = scipy_ent(pk, base=base)
    return ent if isinstance(ent, np.ndarray) else np.array(ent)


def typical_set_cardinality(n: int, pk: Optional[npt.NDArray[Any]] = None, ent: Optional[float] = None,
                            eps: float = 1e-5) -> tuple[float, float]:
    # noinspection LongLine
    """Given a distribution describing an i.i.d process, how many typical sequences of length n are there?

    The cardinality of a typical set is dictated by the AEP. See:
    https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-441-information-theory-spring-2010/lecture-notes/MIT6_441S10_lec03.pdf
    :param n: The length of the sequence
    :param pk: Defaults to None. If specified, a 1d array representing a PMF of a univariate RV.
    :param ent: The entropy of the variable. Defaults to None, in which case it is inferred from distribution.
    If specified, it is used and pk is ignored
    :param eps: The epsilon used for the calculation
    :return: An tuple representing a lower and  upper bounds on the cardinality of the typical set of sequences of length n.
    """
    if n <= 0 or eps <= 0:
        raise ValueError()
    if ent is None:
        if pk is None:
            raise ValueError()
        else:
            ent_f = float(entropy(pk, base=2))
    else:
        ent_f = ent
    ub = 2**(n * (ent_f + eps))
    lb = (1 - eps) * 2**(n * (ent_f - eps))
    return lb, ub
