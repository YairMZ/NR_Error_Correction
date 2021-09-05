import pytest
import numpy as np
from utils.information_theory import prob, entropy


class TestProbability:
    def test_alphabet_size(self):
        data = np.random.randint(10, size=(10, 10))
        p = prob(data, 11)
        assert 11 == p.shape[1]

    def test_multi_dimension(self):
        data = np.random.randint(10, size=(10, 10))
        p = prob(data)
        assert 10 == p.shape[0]

    def test_one_dimension(self):
        data = np.random.randint(10, size=10)
        p = prob(data)
        assert 1 == p.ndim

    def test_probability(self):
        # randint uses a uniform distribution, so for sufficiently large sample, we expect approximately uniform
        data = np.random.randint(5, size=10000000)
        p = prob(data)
        min_val = np.min(p)
        max_val = np.max(p)
        assert 0.2 == pytest.approx(min_val, abs=1e-3)
        assert 0.2 == pytest.approx(max_val, abs=1e-3)

    def test_incompatible_dim(self):
        data = np.array([[[1, 2], [3, 4]], [[1, 2], [3, 4]]])
        with pytest.raises(ValueError):
            prob(data)


class TestEntropy:
    def test_1d_array(self):
        p = np.ones(10)/10
        e = entropy(p)
        assert e == pytest.approx(np.log2(10))
        assert isinstance(e, float)

    def test_2d_array(self):
        p = np.ones((2, 10))/10
        e = entropy(p)
        assert e[0] == pytest.approx(np.log2(10))
        assert e[1] == pytest.approx(np.log2(10))
        assert isinstance(e, np.ndarray)

    def test_zero_mass_probability_1d(self):
        p = np.ones(10) / 9
        p[9] = 0
        e = entropy(p)
        assert e == pytest.approx(np.log2(9))
        assert isinstance(e, float)

    def test_zero_mass_probability_2d(self):
        p = np.ones((2, 10))/9
        p[:, 9] = 0
        e = entropy(p)
        assert e[0] == pytest.approx(np.log2(9))
        assert e[1] == pytest.approx(np.log2(9))
        assert isinstance(e, np.ndarray)

    def test_incompatible_dim(self):
        data = np.array([[[1, 2], [3, 4]], [[1, 2], [3, 4]]])
        with pytest.raises(ValueError):
            entropy(data)
