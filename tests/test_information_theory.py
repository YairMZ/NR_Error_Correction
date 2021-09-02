import unittest
import numpy as np
from utils.information_theory import prob, entropy


class TestProbability(unittest.TestCase):
    def test_alphabet_size(self):
        data = np.random.randint(10, size=(10, 10))
        p = prob(data, 11)
        self.assertEqual(11, p.shape[1])

    def test_multi_dimension(self):
        data = np.random.randint(10, size=(10, 10))
        p = prob(data)
        self.assertEqual(10, p.shape[0])

    def test_one_dimension(self):
        data = np.random.randint(10, size=10)
        p = prob(data)
        self.assertEqual(1, p.ndim)

    def test_probability(self):
        # randint uses a uniform distribution, so for sufficiently large sample, we expect approximately uniform
        data = np.random.randint(5, size=10000000)
        p = prob(data)
        min_val = np.min(p)
        max_val = np.max(p)
        self.assertAlmostEqual(0.2, min_val, 3)
        self.assertAlmostEqual(0.2, max_val, 3)


class TestEntropy(unittest.TestCase):
    def test_1d_array(self):
        p = np.ones(10)/10
        e = entropy(p)
        self.assertAlmostEqual(e, np.log2(10))
        self.assertIsInstance(e, float)

    def test_2d_array(self):
        p = np.ones((2, 10))/10
        e = entropy(p)
        self.assertAlmostEqual(e[0], np.log2(10))
        self.assertAlmostEqual(e[1], np.log2(10))
        self.assertIsInstance(e, np.ndarray)

    def test_zero_mass_probability_1d(self):
        p = np.ones(10) / 9
        p[9] = 0
        e = entropy(p)
        self.assertAlmostEqual(e, np.log2(9))
        self.assertIsInstance(e, float)

    def test_zero_mass_probability_2d(self):
        p = np.ones((2, 10))/9
        p[:, 9] = 0
        e = entropy(p)
        self.assertAlmostEqual(e[0], np.log2(9))
        self.assertAlmostEqual(e[1], np.log2(9))
        self.assertIsInstance(e, np.ndarray)


if __name__ == '__main__':
    unittest.main()
