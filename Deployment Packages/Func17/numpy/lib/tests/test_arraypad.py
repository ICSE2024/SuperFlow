"""Tests for the array padding functions.

"""
from __future__ import division, absolute_import, print_function

import pytest

import numpy as np
from numpy.testing import (assert_array_equal, assert_raises, assert_allclose,
                           assert_equal)
from numpy.lib import pad
from numpy.lib.arraypad import _as_pairs


class TestAsPairs(object):

    def test_single_value(self):
        """Test casting for a single value."""
        expected = np.array([[3, 3]] * 10)
        for x in (3, [3], [[3]]):
            result = _as_pairs(x, 10)
            assert_equal(result, expected)
        # Test with dtype=object
        obj = object()
        assert_equal(
            _as_pairs(obj, 10),
            np.array([[obj, obj]] * 10)
        )

    def test_two_values(self):
        """Test proper casting for two different values."""
        # Broadcasting in the first dimension with numbers
        expected = np.array([[3, 4]] * 10)
        for x in ([3, 4], [[3, 4]]):
            result = _as_pairs(x, 10)
            assert_equal(result, expected)
        # and with dtype=object
        obj = object()
        assert_equal(
            _as_pairs(["a", obj], 10),
            np.array([["a", obj]] * 10)
        )

        # Broadcasting in the second / last dimension with numbers
        assert_equal(
            _as_pairs([[3], [4]], 2),
            np.array([[3, 3], [4, 4]])
        )
        # and with dtype=object
        assert_equal(
            _as_pairs([["a"], [obj]], 2),
            np.array([["a", "a"], [obj, obj]])
        )

    def test_with_none(self):
        expected = ((None, None), (None, None), (None, None))
        assert_equal(
            _as_pairs(None, 3, as_index=False),
            expected
        )
        assert_equal(
            _as_pairs(None, 3, as_index=True),
            expected
        )

    def test_pass_through(self):
        """Test if `x` already matching desired output are passed through."""
        expected = np.arange(12).reshape((6, 2))
        assert_equal(
            _as_pairs(expected, 6),
            expected
        )

    def test_as_index(self):
        """Test results if `as_index=True`."""
        assert_equal(
            _as_pairs([2.6, 3.3], 10, as_index=True),
            np.array([[3, 3]] * 10, dtype=np.intp)
        )
        assert_equal(
            _as_pairs([2.6, 4.49], 10, as_index=True),
            np.array([[3, 4]] * 10, dtype=np.intp)
        )
        for x in (-3, [-3], [[-3]], [-3, 4], [3, -4], [[-3, 4]], [[4, -3]],
                  [[1, 2]] * 9 + [[1, -2]]):
            with pytest.raises(ValueError, match="negative values"):
                _as_pairs(x, 10, as_index=True)

    def test_exceptions(self):
        """Ensure faulty usage is discovered."""
        with pytest.raises(ValueError, match="more dimensions than allowed"):
            _as_pairs([[[3]]], 10)
        with pytest.raises(ValueError, match="could not be broadcast"):
            _as_pairs([[1, 2], [3, 4]], 3)
        with pytest.raises(ValueError, match="could not be broadcast"):
            _as_pairs(np.ones((2, 3)), 3)


class TestConditionalShortcuts(object):
    def test_zero_padding_shortcuts(self):
        test = np.arange(120).reshape(4, 5, 6)
        pad_amt = [(0, 0) for axis in test.shape]
        modes = ['constant',
                 'edge',
                 'linear_ramp',
                 'maximum',
                 'mean',
                 'median',
                 'minimum',
                 'reflect',
                 'symmetric',
                 'wrap',
                 ]
        for mode in modes:
            assert_array_equal(test, pad(test, pad_amt, mode=mode))

    def test_shallow_statistic_range(self):
        test = np.arange(120).reshape(4, 5, 6)
        pad_amt = [(1, 1) for axis in test.shape]
        modes = ['maximum',
                 'mean',
                 'median',
                 'minimum',
                 ]
        for mode in modes:
            assert_array_equal(pad(test, pad_amt, mode='edge'),
                               pad(test, pad_amt, mode=mode, stat_length=1))

    def test_clip_statistic_range(self):
        test = np.arange(30).reshape(5, 6)
        pad_amt = [(3, 3) for axis in test.shape]
        modes = ['maximum',
                 'mean',
                 'median',
                 'minimum',
                 ]
        for mode in modes:
            assert_array_equal(pad(test, pad_amt, mode=mode),
                               pad(test, pad_amt, mode=mode, stat_length=30))


class TestStatistic(object):
    def test_check_mean_stat_length(self):
        a = np.arange(100).astype('f')
        a = pad(a, ((25, 20), ), 'mean', stat_length=((2, 3), ))
        b = np.array(
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
             0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
             0.5, 0.5, 0.5, 0.5, 0.5,

             0., 1., 2., 3., 4., 5., 6., 7., 8., 9.,
             10., 11., 12., 13., 14., 15., 16., 17., 18., 19.,
             20., 21., 22., 23., 24., 25., 26., 27., 28., 29.,
             30., 31., 32., 33., 34., 35., 36., 37., 38., 39.,
             40., 41., 42., 43., 44., 45., 46., 47., 48., 49.,
             50., 51., 52., 53., 54., 55., 56., 57., 58., 59.,
             60., 61., 62., 63., 64., 65., 66., 67., 68., 69.,
             70., 71., 72., 73., 74., 75., 76., 77., 78., 79.,
             80., 81., 82., 83., 84., 85., 86., 87., 88., 89.,
             90., 91., 92., 93., 94., 95., 96., 97., 98., 99.,

             98., 98., 98., 98., 98., 98., 98., 98., 98., 98.,
             98., 98., 98., 98., 98., 98., 98., 98., 98., 98.
             ])
        assert_array_equal(a, b)

    def test_check_maximum_1(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'maximum')
        b = np.array(
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
             99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
             99, 99, 99, 99, 99,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             99, 99, 99, 99, 99, 99, 99, 99, 99, 99,
             99, 99, 99, 99, 99, 99, 99, 99, 99, 99]
            )
        assert_array_equal(a, b)

    def test_check_maximum_2(self):
        a = np.arange(100) + 1
        a = pad(a, (25, 20), 'maximum')
        b = np.array(
            [100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
             100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
             100, 100, 100, 100, 100,

             1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
             11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
             31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
             41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
             51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
             61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
             71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
             81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
             91, 92, 93, 94, 95, 96, 97, 98, 99, 100,

             100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
             100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
            )
        assert_array_equal(a, b)

    def test_check_maximum_stat_length(self):
        a = np.arange(100) + 1
        a = pad(a, (25, 20), 'maximum', stat_length=10)
        b = np.array(
            [10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
             10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
             10, 10, 10, 10, 10,

              1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
             11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
             31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
             41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
             51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
             61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
             71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
             81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
             91, 92, 93, 94, 95, 96, 97, 98, 99, 100,

             100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
             100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
            )
        assert_array_equal(a, b)

    def test_check_minimum_1(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'minimum')
        b = np.array(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            )
        assert_array_equal(a, b)

    def test_check_minimum_2(self):
        a = np.arange(100) + 2
        a = pad(a, (25, 20), 'minimum')
        b = np.array(
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2,

             2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
             12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
             22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
             32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
             42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
             52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
             62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
             72, 73, 74, 75, 76, 77, 78, 79, 80, 81,
             82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
             92, 93, 94, 95, 96, 97, 98, 99, 100, 101,

             2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
             2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
            )
        assert_array_equal(a, b)

    def test_check_minimum_stat_length(self):
        a = np.arange(100) + 1
        a = pad(a, (25, 20), 'minimum', stat_length=10)
        b = np.array(
            [ 1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
              1,  1,  1,  1,  1,  1,  1,  1,  1,  1,
              1,  1,  1,  1,  1,

              1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
             11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
             31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
             41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
             51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
             61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
             71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
             81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
             91, 92, 93, 94, 95, 96, 97, 98, 99, 100,

             91, 91, 91, 91, 91, 91, 91, 91, 91, 91,
             91, 91, 91, 91, 91, 91, 91, 91, 91, 91]
            )
        assert_array_equal(a, b)

    def test_check_median(self):
        a = np.arange(100).astype('f')
        a = pad(a, (25, 20), 'median')
        b = np.array(
            [49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5,
             49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5,
             49.5, 49.5, 49.5, 49.5, 49.5,

             0., 1., 2., 3., 4., 5., 6., 7., 8., 9.,
             10., 11., 12., 13., 14., 15., 16., 17., 18., 19.,
             20., 21., 22., 23., 24., 25., 26., 27., 28., 29.,
             30., 31., 32., 33., 34., 35., 36., 37., 38., 39.,
             40., 41., 42., 43., 44., 45., 46., 47., 48., 49.,
             50., 51., 52., 53., 54., 55., 56., 57., 58., 59.,
             60., 61., 62., 63., 64., 65., 66., 67., 68., 69.,
             70., 71., 72., 73., 74., 75., 76., 77., 78., 79.,
             80., 81., 82., 83., 84., 85., 86., 87., 88., 89.,
             90., 91., 92., 93., 94., 95., 96., 97., 98., 99.,

             49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5,
             49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5]
            )
        assert_array_equal(a, b)

    def test_check_median_01(self):
        a = np.array([[3, 1, 4], [4, 5, 9], [9, 8, 2]])
        a = pad(a, 1, 'median')
        b = np.array(
            [[4, 4, 5, 4, 4],

             [3, 3, 1, 4, 3],
             [5, 4, 5, 9, 5],
             [8, 9, 8, 2, 8],

             [4, 4, 5, 4, 4]]
            )
        assert_array_equal(a, b)

    def test_check_median_02(self):
        a = np.array([[3, 1, 4], [4, 5, 9], [9, 8, 2]])
        a = pad(a.T, 1, 'median').T
        b = np.array(
            [[5, 4, 5, 4, 5],

             [3, 3, 1, 4, 3],
             [5, 4, 5, 9, 5],
             [8, 9, 8, 2, 8],

             [5, 4, 5, 4, 5]]
            )
        assert_array_equal(a, b)

    def test_check_median_stat_length(self):
        a = np.arange(100).astype('f')
        a[1] = 2.
        a[97] = 96.
        a = pad(a, (25, 20), 'median', stat_length=(3, 5))
        b = np.array(
            [ 2.,  2.,  2.,  2.,  2.,  2.,  2.,  2.,  2.,  2.,
              2.,  2.,  2.,  2.,  2.,  2.,  2.,  2.,  2.,  2.,
              2.,  2.,  2.,  2.,  2.,

              0.,  2.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9.,
             10., 11., 12., 13., 14., 15., 16., 17., 18., 19.,
             20., 21., 22., 23., 24., 25., 26., 27., 28., 29.,
             30., 31., 32., 33., 34., 35., 36., 37., 38., 39.,
             40., 41., 42., 43., 44., 45., 46., 47., 48., 49.,
             50., 51., 52., 53., 54., 55., 56., 57., 58., 59.,
             60., 61., 62., 63., 64., 65., 66., 67., 68., 69.,
             70., 71., 72., 73., 74., 75., 76., 77., 78., 79.,
             80., 81., 82., 83., 84., 85., 86., 87., 88., 89.,
             90., 91., 92., 93., 94., 95., 96., 96., 98., 99.,

             96., 96., 96., 96., 96., 96., 96., 96., 96., 96.,
             96., 96., 96., 96., 96., 96., 96., 96., 96., 96.]
            )
        assert_array_equal(a, b)

    def test_check_mean_shape_one(self):
        a = [[4, 5, 6]]
        a = pad(a, (5, 7), 'mean', stat_length=2)
        b = np.array(
            [[4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],

             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],

             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6],
             [4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6]]
            )
        assert_array_equal(a, b)

    def test_check_mean_2(self):
        a = np.arange(100).astype('f')
        a = pad(a, (25, 20), 'mean')
        b = np.array(
            [49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5,
             49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5,
             49.5, 49.5, 49.5, 49.5, 49.5,

             0., 1., 2., 3., 4., 5., 6., 7., 8., 9.,
             10., 11., 12., 13., 14., 15., 16., 17., 18., 19.,
             20., 21., 22., 23., 24., 25., 26., 27., 28., 29.,
             30., 31., 32., 33., 34., 35., 36., 37., 38., 39.,
             40., 41., 42., 43., 44., 45., 46., 47., 48., 49.,
             50., 51., 52., 53., 54., 55., 56., 57., 58., 59.,
             60., 61., 62., 63., 64., 65., 66., 67., 68., 69.,
             70., 71., 72., 73., 74., 75., 76., 77., 78., 79.,
             80., 81., 82., 83., 84., 85., 86., 87., 88., 89.,
             90., 91., 92., 93., 94., 95., 96., 97., 98., 99.,

             49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5,
             49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5, 49.5]
            )
        assert_array_equal(a, b)

    @pytest.mark.parametrize("mode", [
        pytest.param("mean", marks=pytest.mark.xfail(reason="gh-11216")),
        "median",
        "minimum",
        "maximum"
    ])
    def test_same_prepend_append(self, mode):
        """ Test that appended and prepended values are equal """
        # This test is constructed to trigger floating point rounding errors in
        # a way that caused gh-11216 for mode=='mean'
        a = np.array([-1, 2, -1]) + np.array([0, 1e-12, 0], dtype=np.float64)
        a = np.pad(a, (1, 1), mode)
        assert_equal(a[0], a[-1])


class TestConstant(object):
    def test_check_constant(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'constant', constant_values=(10, 20))
        b = np.array(
            [10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
             10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
             10, 10, 10, 10, 10,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
             20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
            )
        assert_array_equal(a, b)

    def test_check_constant_zeros(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'constant')
        b = np.array(
            [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
              0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
              0,  0,  0,  0,  0,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

              0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
              0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
            )
        assert_array_equal(a, b)

    def test_check_constant_float(self):
        # If input array is int, but constant_values are float, the dtype of
        # the array to be padded is kept
        arr = np.arange(30).reshape(5, 6)
        test = pad(arr, (1, 2), mode='constant',
                   constant_values=1.1)
        expected = np.array(
            [[ 1,  1,  1,  1,  1,  1,  1,  1,  1],

             [ 1,  0,  1,  2,  3,  4,  5,  1,  1],
             [ 1,  6,  7,  8,  9, 10, 11,  1,  1],
             [ 1, 12, 13, 14, 15, 16, 17,  1,  1],
             [ 1, 18, 19, 20, 21, 22, 23,  1,  1],
             [ 1, 24, 25, 26, 27, 28, 29,  1,  1],

             [ 1,  1,  1,  1,  1,  1,  1,  1,  1],
             [ 1,  1,  1,  1,  1,  1,  1,  1,  1]]
            )
        assert_allclose(test, expected)

    def test_check_constant_float2(self):
        # If input array is float, and constant_values are float, the dtype of
        # the array to be padded is kept - here retaining the float constants
        arr = np.arange(30).reshape(5, 6)
        arr_float = arr.astype(np.float64)
        test = pad(arr_float, ((1, 2), (1, 2)), mode='constant',
                   constant_values=1.1)
        expected = np.array(
            [[  1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1],

             [  1.1,   0. ,   1. ,   2. ,   3. ,   4. ,   5. ,   1.1,   1.1],
             [  1.1,   6. ,   7. ,   8. ,   9. ,  10. ,  11. ,   1.1,   1.1],
             [  1.1,  12. ,  13. ,  14. ,  15. ,  16. ,  17. ,   1.1,   1.1],
             [  1.1,  18. ,  19. ,  20. ,  21. ,  22. ,  23. ,   1.1,   1.1],
             [  1.1,  24. ,  25. ,  26. ,  27. ,  28. ,  29. ,   1.1,   1.1],

             [  1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1],
             [  1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1,   1.1]]
            )
        assert_allclose(test, expected)

    def test_check_constant_float3(self):
        a = np.arange(100, dtype=float)
        a = pad(a, (25, 20), 'constant', constant_values=(-1.1, -1.2))
        b = np.array(
            [-1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1,
             -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1, -1.1,
             -1.1, -1.1, -1.1, -1.1, -1.1,

             0,  1,  2,  3,  4,  5,  6,  7,  8,  9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2,
             -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2, -1.2]
            )
        assert_allclose(a, b)

    def test_check_constant_odd_pad_amount(self):
        arr = np.arange(30).reshape(5, 6)
        test = pad(arr, ((1,), (2,)), mode='constant',
                   constant_values=3)
        expected = np.array(
            [[ 3,  3,  3,  3,  3,  3,  3,  3,  3,  3],

             [ 3,  3,  0,  1,  2,  3,  4,  5,  3,  3],
             [ 3,  3,  6,  7,  8,  9, 10, 11,  3,  3],
             [ 3,  3, 12, 13, 14, 15, 16, 17,  3,  3],
             [ 3,  3, 18, 19, 20, 21, 22, 23,  3,  3],
             [ 3,  3, 24, 25, 26, 27, 28, 29,  3,  3],

             [ 3,  3,  3,  3,  3,  3,  3,  3,  3,  3]]
            )
        assert_allclose(test, expected)

    def test_check_constant_pad_2d(self):
        arr = np.arange(4).reshape(2, 2)
        test = np.lib.pad(arr, ((1, 2), (1, 3)), mode='constant',
                          constant_values=((1, 2), (3, 4)))
        expected = np.array(
            [[3, 1, 1, 4, 4, 4],
             [3, 0, 1, 4, 4, 4],
             [3, 2, 3, 4, 4, 4],
             [3, 2, 2, 4, 4, 4],
             [3, 2, 2, 4, 4, 4]]
        )
        assert_allclose(test, expected)

    def test_check_large_integers(self):
        uint64_max = 2 ** 64 - 1
        arr = np.full(5, uint64_max, dtype=np.uint64)
        test = np.pad(arr, 1, mode="constant", constant_values=arr.min())
        expected = np.full(7, uint64_max, dtype=np.uint64)
        assert_array_equal(test, expected)

        int64_max = 2 ** 63 - 1
        arr = np.full(5, int64_max, dtype=np.int64)
        test = np.pad(arr, 1, mode="constant", constant_values=arr.min())
        expected = np.full(7, int64_max, dtype=np.int64)
        assert_array_equal(test, expected)

    def test_check_object_array(self):
        arr = np.empty(1, dtype=object)
        obj_a = object()
        arr[0] = obj_a
        obj_b = object()
        obj_c = object()
        arr = np.pad(arr, pad_width=1, mode='constant',
                     constant_values=(obj_b, obj_c))

        expected = np.empty((3,), dtype=object)
        expected[0] = obj_b
        expected[1] = obj_a
        expected[2] = obj_c

        assert_array_equal(arr, expected)


class TestLinearRamp(object):
    def test_check_simple(self):
        a = np.arange(100).astype('f')
        a = pad(a, (25, 20), 'linear_ramp', end_values=(4, 5))
        b = np.array(
            [4.00, 3.84, 3.68, 3.52, 3.36, 3.20, 3.04, 2.88, 2.72, 2.56,
             2.40, 2.24, 2.08, 1.92, 1.76, 1.60, 1.44, 1.28, 1.12, 0.96,
             0.80, 0.64, 0.48, 0.32, 0.16,

             0.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 9.00,
             10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0,
             20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0,
             30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0,
             40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0,
             50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0,
             60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0,
             70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0,
             80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0,
             90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0,

             94.3, 89.6, 84.9, 80.2, 75.5, 70.8, 66.1, 61.4, 56.7, 52.0,
             47.3, 42.6, 37.9, 33.2, 28.5, 23.8, 19.1, 14.4, 9.7, 5.]
            )
        assert_allclose(a, b, rtol=1e-5, atol=1e-5)

    def test_check_2d(self):
        arr = np.arange(20).reshape(4, 5).astype(np.float64)
        test = pad(arr, (2, 2), mode='linear_ramp', end_values=(0, 0))
        expected = np.array(
            [[0.,   0.,   0.,   0.,   0.,   0.,   0.,    0.,   0.],
             [0.,   0.,   0.,  0.5,   1.,  1.5,   2.,    1.,   0.],
             [0.,   0.,   0.,   1.,   2.,   3.,   4.,    2.,   0.],
             [0.,  2.5,   5.,   6.,   7.,   8.,   9.,   4.5,   0.],
             [0.,   5.,  10.,  11.,  12.,  13.,  14.,    7.,   0.],
             [0.,  7.5,  15.,  16.,  17.,  18.,  19.,   9.5,   0.],
             [0., 3.75,  7.5,   8.,  8.5,   9.,  9.5,  4.75,   0.],
             [0.,   0.,   0.,   0.,   0.,   0.,   0.,    0.,   0.]])
        assert_allclose(test, expected)

    @pytest.mark.xfail(exceptions=(AssertionError,))
    def test_object_array(self):
        from fractions import Fraction
        arr = np.array([Fraction(1, 2), Fraction(-1, 2)])
        actual = np.pad(arr, (2, 3), mode='linear_ramp', end_values=0)

        # deliberately chosen to have a non-power-of-2 denominator such that
        # rounding to floats causes a failure.
        expected = np.array([
            Fraction( 0, 12),
            Fraction( 3, 12),
            Fraction( 6, 12),
            Fraction(-6, 12),
            Fraction(-4, 12),
            Fraction(-2, 12),
            Fraction(-0, 12),
        ])
        assert_equal(actual, expected)

    @pytest.mark.parametrize("dtype", (
        np.sctypes["uint"]
        + np.sctypes["int"]
        + np.sctypes["float"]
        + np.sctypes["complex"]
    ))
    def test_negative_difference(self, dtype):
        """
        Check correct behavior of unsigned dtypes if there is a negative
        difference between the edge to pad and `end_values`. Check both cases
        to be independent of implementation. Test behavior for all other dtypes
        in case dtype casting interferes with complex dtypes. See gh-14191.
        """
        x = np.array([3], dtype=dtype)
        result = np.pad(x, 3, mode="linear_ramp", end_values=0)
        expected = np.array([0, 1, 2, 3, 2, 1, 0], dtype=dtype)
        assert_equal(result, expected)

        x = np.array([0], dtype=dtype)
        result = np.pad(x, 3, mode="linear_ramp", end_values=3)
        expected = np.array([3, 2, 1, 0, 1, 2, 3], dtype=dtype)
        assert_equal(result, expected)



class TestReflect(object):
    def test_check_simple(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'reflect')
        b = np.array(
            [25, 24, 23, 22, 21, 20, 19, 18, 17, 16,
             15, 14, 13, 12, 11, 10, 9, 8, 7, 6,
             5, 4, 3, 2, 1,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             98, 97, 96, 95, 94, 93, 92, 91, 90, 89,
             88, 87, 86, 85, 84, 83, 82, 81, 80, 79]
            )
        assert_array_equal(a, b)

    def test_check_odd_method(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'reflect', reflect_type='odd')
        b = np.array(
            [-25, -24, -23, -22, -21, -20, -19, -18, -17, -16,
             -15, -14, -13, -12, -11, -10, -9, -8, -7, -6,
             -5, -4, -3, -2, -1,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
             110, 111, 112, 113, 114, 115, 116, 117, 118, 119]
            )
        assert_array_equal(a, b)

    def test_check_large_pad(self):
        a = [[4, 5, 6], [6, 7, 8]]
        a = pad(a, (5, 7), 'reflect')
        b = np.array(
            [[7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],

             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],

             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7, 8, 7, 6, 7],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5]]
            )
        assert_array_equal(a, b)

    def test_check_shape(self):
        a = [[4, 5, 6]]
        a = pad(a, (5, 7), 'reflect')
        b = np.array(
            [[5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],

             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],

             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5],
             [5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5, 6, 5, 4, 5]]
            )
        assert_array_equal(a, b)

    def test_check_01(self):
        a = pad([1, 2, 3], 2, 'reflect')
        b = np.array([3, 2, 1, 2, 3, 2, 1])
        assert_array_equal(a, b)

    def test_check_02(self):
        a = pad([1, 2, 3], 3, 'reflect')
        b = np.array([2, 3, 2, 1, 2, 3, 2, 1, 2])
        assert_array_equal(a, b)

    def test_check_03(self):
        a = pad([1, 2, 3], 4, 'reflect')
        b = np.array([1, 2, 3, 2, 1, 2, 3, 2, 1, 2, 3])
        assert_array_equal(a, b)

    def test_check_padding_an_empty_array(self):
        a = pad(np.zeros((0, 3)), ((0,), (1,)), mode='reflect')
        b = np.zeros((0, 5))
        assert_array_equal(a, b)


class TestSymmetric(object):
    def test_check_simple(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'symmetric')
        b = np.array(
            [24, 23, 22, 21, 20, 19, 18, 17, 16, 15,
             14, 13, 12, 11, 10, 9, 8, 7, 6, 5,
             4, 3, 2, 1, 0,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             99, 98, 97, 96, 95, 94, 93, 92, 91, 90,
             89, 88, 87, 86, 85, 84, 83, 82, 81, 80]
            )
        assert_array_equal(a, b)

    def test_check_odd_method(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'symmetric', reflect_type='odd')
        b = np.array(
            [-24, -23, -22, -21, -20, -19, -18, -17, -16, -15,
             -14, -13, -12, -11, -10, -9, -8, -7, -6, -5,
             -4, -3, -2, -1, 0,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             99, 100, 101, 102, 103, 104, 105, 106, 107, 108,
             109, 110, 111, 112, 113, 114, 115, 116, 117, 118]
            )
        assert_array_equal(a, b)

    def test_check_large_pad(self):
        a = [[4, 5, 6], [6, 7, 8]]
        a = pad(a, (5, 7), 'symmetric')
        b = np.array(
            [[5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [7, 8, 8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8, 8],
             [7, 8, 8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8, 8],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],

             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [7, 8, 8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8, 8],

             [7, 8, 8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8, 8],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [7, 8, 8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8, 8],
             [7, 8, 8, 7, 6, 6, 7, 8, 8, 7, 6, 6, 7, 8, 8],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6]]
            )

        assert_array_equal(a, b)

    def test_check_large_pad_odd(self):
        a = [[4, 5, 6], [6, 7, 8]]
        a = pad(a, (5, 7), 'symmetric', reflect_type='odd')
        b = np.array(
            [[-3, -2, -2, -1,  0,  0,  1,  2,  2,  3,  4,  4,  5,  6,  6],
             [-3, -2, -2, -1,  0,  0,  1,  2,  2,  3,  4,  4,  5,  6,  6],
             [-1,  0,  0,  1,  2,  2,  3,  4,  4,  5,  6,  6,  7,  8,  8],
             [-1,  0,  0,  1,  2,  2,  3,  4,  4,  5,  6,  6,  7,  8,  8],
             [ 1,  2,  2,  3,  4,  4,  5,  6,  6,  7,  8,  8,  9, 10, 10],

             [ 1,  2,  2,  3,  4,  4,  5,  6,  6,  7,  8,  8,  9, 10, 10],
             [ 3,  4,  4,  5,  6,  6,  7,  8,  8,  9, 10, 10, 11, 12, 12],

             [ 3,  4,  4,  5,  6,  6,  7,  8,  8,  9, 10, 10, 11, 12, 12],
             [ 5,  6,  6,  7,  8,  8,  9, 10, 10, 11, 12, 12, 13, 14, 14],
             [ 5,  6,  6,  7,  8,  8,  9, 10, 10, 11, 12, 12, 13, 14, 14],
             [ 7,  8,  8,  9, 10, 10, 11, 12, 12, 13, 14, 14, 15, 16, 16],
             [ 7,  8,  8,  9, 10, 10, 11, 12, 12, 13, 14, 14, 15, 16, 16],
             [ 9, 10, 10, 11, 12, 12, 13, 14, 14, 15, 16, 16, 17, 18, 18],
             [ 9, 10, 10, 11, 12, 12, 13, 14, 14, 15, 16, 16, 17, 18, 18]]
            )
        assert_array_equal(a, b)

    def test_check_shape(self):
        a = [[4, 5, 6]]
        a = pad(a, (5, 7), 'symmetric')
        b = np.array(
            [[5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],

             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],

             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6],
             [5, 6, 6, 5, 4, 4, 5, 6, 6, 5, 4, 4, 5, 6, 6]]
            )
        assert_array_equal(a, b)

    def test_check_01(self):
        a = pad([1, 2, 3], 2, 'symmetric')
        b = np.array([2, 1, 1, 2, 3, 3, 2])
        assert_array_equal(a, b)

    def test_check_02(self):
        a = pad([1, 2, 3], 3, 'symmetric')
        b = np.array([3, 2, 1, 1, 2, 3, 3, 2, 1])
        assert_array_equal(a, b)

    def test_check_03(self):
        a = pad([1, 2, 3], 6, 'symmetric')
        b = np.array([1, 2, 3, 3, 2, 1, 1, 2, 3, 3, 2, 1, 1, 2, 3])
        assert_array_equal(a, b)


class TestWrap(object):
    def test_check_simple(self):
        a = np.arange(100)
        a = pad(a, (25, 20), 'wrap')
        b = np.array(
            [75, 76, 77, 78, 79, 80, 81, 82, 83, 84,
             85, 86, 87, 88, 89, 90, 91, 92, 93, 94,
             95, 96, 97, 98, 99,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
             30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
             40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
             60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
             70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
             90, 91, 92, 93, 94, 95, 96, 97, 98, 99,

             0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
             10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
            )
        assert_array_equal(a, b)

    def test_check_large_pad(self):
        a = np.arange(12)
        a = np.reshape(a, (3, 4))
        a = pad(a, (10, 12), 'wrap')
        b = np.array(
            [[10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],
             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],
             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],
             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],

             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],

             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],
             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],
             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11],
             [2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2,
              3, 0, 1, 2, 3, 0, 1, 2, 3],
             [6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6, 7, 4, 5, 6,
              7, 4, 5, 6, 7, 4, 5, 6, 7],
             [10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10, 11, 8, 9, 10,
              11, 8, 9, 10, 11, 8, 9, 10, 11]]
            )
        assert_array_equal(a, b)

    def test_check_01(self):
        a = pad([1, 2, 3], 3, 'wrap')
        b = np.array([1, 2, 3, 1, 2, 3, 1, 2, 3])
        assert_array_equal(a, b)

    def test_check_02(self):
        a = pad([1, 2, 3], 4, 'wrap')
        b = np.array([3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1])
        assert_array_equal(a, b)

    def test_pad_with_zero(self):
        a = np.ones((3, 5))
        b = np.pad(a, (0, 5), mode="wrap")
        assert_array_equal(a, b[:-5, :-5])


class TestStatLen(object):
    def test_check_simple(self):
        a = np.arange(30)
        a = np.reshape(a, (6, 5))
        a = pad(a, ((2, 3), (3, 2)), mode='mean', stat_length=(3,))
        b = np.array(
            [[6, 6, 6, 5, 6, 7, 8, 9, 8, 8],
             [6, 6, 6, 5, 6, 7, 8, 9, 8, 8],

             [1, 1, 1, 0, 1, 2, 3, 4, 3, 3],
             [6, 6, 6, 5, 6, 7, 8, 9, 8, 8],
             [11, 11, 11, 10, 11, 12, 13, 14, 13, 13],
             [16, 16, 16, 15, 16, 17, 18, 19, 18, 18],
             [21, 21, 21, 20, 21, 22, 23, 24, 23, 23],
             [26, 26, 26, 25, 26, 27, 28, 29, 28, 28],

             [21, 21, 21, 20, 21, 22, 23, 24, 23, 23],
             [21, 21, 21, 20, 21, 22, 23, 24, 23, 23],
             [21, 21, 21, 20, 21, 22, 23, 24, 23, 23]]
            )
        assert_array_equal(a, b)


class TestEdge(object):
    def test_check_simple(self):
        a = np.arange(12)
        a = np.reshape(a, (4, 3))
        a = pad(a, ((2, 3), (3, 2)), 'edge')
        b = np.array(
            [[0, 0, 0, 0, 1, 2, 2, 2],
             [0, 0, 0, 0, 1, 2, 2, 2],

             [0, 0, 0, 0, 1, 2, 2, 2],
             [3, 3, 3, 3, 4, 5, 5, 5],
             [6, 6, 6, 6, 7, 8, 8, 8],
             [9, 9, 9, 9, 10, 11, 11, 11],

             [9, 9, 9, 9, 10, 11, 11, 11],
             [9, 9, 9, 9, 10, 11, 11, 11],
             [9, 9, 9, 9, 10, 11, 11, 11]]
            )
        assert_array_equal(a, b)

    def test_check_width_shape_1_2(self):
        # Check a pad_width of the form ((1, 2),).
        # Regression test for issue gh-7808.
        a = np.array([1, 2, 3])
        padded = pad(a, ((1, 2),), 'edge')
        expected = np.array([1, 1, 2, 3, 3, 3])
        assert_array_equal(padded, expected)

        a = np.array([[1, 2, 3], [4, 5, 6]])
        padded = pad(a, ((1, 2),), 'edge')
        expected = pad(a, ((1, 2), (1, 2)), 'edge')
        assert_array_equal(padded, expected)

        a = np.arange(24).reshape(2, 3, 4)
        padded = pad(a, ((1, 2),), 'edge')
        expected = pad(a, ((1, 2), (1, 2), (1, 2)), 'edge')
        assert_array_equal(padded, expected)


class TestZeroPadWidth(object):
    def test_zero_pad_width(self):
        arr = np.arange(30)
        arr = np.reshape(arr, (6, 5))
        for pad_width in (0, (0, 0), ((0, 0), (0, 0))):
            assert_array_equal(arr, pad(arr, pad_width, mode='constant'))


class TestLegacyVectorFunction(object):
    def test_legacy_vector_functionality(self):
        def _padwithtens(vector, pad_width, iaxis, kwargs):
            vector[:pad_width[0]] = 10
            vector[-pad_width[1]:] = 10
            return vector

        a = np.arange(6).reshape(2, 3)
        a = pad(a, 2, _padwithtens)
        b = np.array(
            [[10, 10, 10, 10, 10, 10, 10],
             [10, 10, 10, 10, 10, 10, 10],

             [10, 10,  0,  1,  2, 10, 10],
             [10, 10,  3,  4,  5, 10, 10],

             [10, 10, 10, 10, 10, 10, 10],
             [10, 10, 10, 10, 10, 10, 10]]
            )
        assert_array_equal(a, b)


class TestNdarrayPadWidth(object):
    def test_check_simple(self):
        a = np.arange(12)
        a = np.reshape(a, (4, 3))
        a = pad(a, np.array(((2, 3), (3, 2))), 'edge')
        b = np.array(
            [[0,  0,  0,    0,  1,  2,    2,  2],
             [0,  0,  0,    0,  1,  2,    2,  2],

             [0,  0,  0,    0,  1,  2,    2,  2],
             [3,  3,  3,    3,  4,  5,    5,  5],
             [6,  6,  6,    6,  7,  8,    8,  8],
             [9,  9,  9,    9, 10, 11,   11, 11],

             [9,  9,  9,    9, 10, 11,   11, 11],
             [9,  9,  9,    9, 10, 11,   11, 11],
             [9,  9,  9,    9, 10, 11,   11, 11]]
            )
        assert_array_equal(a, b)


class TestUnicodeInput(object):
    def test_unicode_mode(self):
        constant_mode = u'constant'
        a = np.pad([1], 2, mode=constant_mode)
        b = np.array([0, 0, 1, 0, 0])
        assert_array_equal(a, b)


class TestObjectInput(object):
    def test_object_input(self):
        # Regression test for issue gh-11395.
        a = np.full((4, 3), None)
        pad_amt = ((2, 3), (3, 2))
        b = np.full((9, 8), None)
        modes = ['edge',
                 'symmetric',
                 'reflect',
                 'wrap',
                 ]
        for mode in modes:
            assert_array_equal(pad(a, pad_amt, mode=mode), b)


class TestValueError1(object):
    def test_check_simple(self):
        arr = np.arange(30)
        arr = np.reshape(arr, (6, 5))
        kwargs = dict(mode='mean', stat_length=(3, ))
        assert_raises(ValueError, pad, arr, ((2, 3), (3, 2), (4, 5)),
                      **kwargs)

    def test_check_negative_stat_length(self):
        arr = np.arange(30)
        arr = np.reshape(arr, (6, 5))
        kwargs = dict(mode='mean', stat_length=(-3, ))
        assert_raises(ValueError, pad, arr, ((2, 3), (3, 2)),
                      **kwargs)

    def test_check_negative_pad_width(self):
        arr = np.arange(30)
        arr = np.reshape(arr, (6, 5))
        kwargs = dict(mode='mean', stat_length=(3, ))
        assert_raises(ValueError, pad, arr, ((-2, 3), (3, 2)),
                      **kwargs)

    def test_check_empty_array(self):
        assert_raises(ValueError, pad, [], 4, mode='reflect')
        assert_raises(ValueError, pad, np.ndarray(0), 4, mode='reflect')
        assert_raises(ValueError, pad, np.zeros((0, 3)), ((1,), (0,)),
                      mode='reflect')


class TestValueError2(object):
    def test_check_negative_pad_amount(self):
        arr = np.arange(30)
        arr = np.reshape(arr, (6, 5))
        kwargs = dict(mode='mean', stat_length=(3, ))
        assert_raises(ValueError, pad, arr, ((-2, 3), (3, 2)),
                      **kwargs)


class TestValueError3(object):
    def test_check_kwarg_not_allowed(self):
        arr = np.arange(30).reshape(5, 6)
        assert_raises(ValueError, pad, arr, 4, mode='mean',
                      reflect_type='odd')

    def test_mode_not_set(self):
        arr = np.arange(30).reshape(5, 6)
        assert_raises(TypeError, pad, arr, 4)

    def test_malformed_pad_amount(self):
        arr = np.arange(30).reshape(5, 6)
        assert_raises(ValueError, pad, arr, (4, 5, 6, 7), mode='constant')

    def test_malformed_pad_amount2(self):
        arr = np.arange(30).reshape(5, 6)
        assert_raises(ValueError, pad, arr, ((3, 4, 5), (0, 1, 2)),
                      mode='constant')

    def test_pad_too_many_axes(self):
        arr = np.arange(30).reshape(5, 6)

        # Attempt to pad using a 3D array equivalent
        bad_shape = (((3,), (4,), (5,)), ((0,), (1,), (2,)))
        assert_raises(ValueError, pad, arr, bad_shape,
                      mode='constant')


class TestTypeError1(object):
    def test_float(self):
        arr = np.arange(30)
        assert_raises(TypeError, pad, arr, ((-2.1, 3), (3, 2)))
        assert_raises(TypeError, pad, arr, np.array(((-2.1, 3), (3, 2))))

    def test_str(self):
        arr = np.arange(30)
        assert_raises(TypeError, pad, arr, 'foo')
        assert_raises(TypeError, pad, arr, np.array('foo'))

    def test_object(self):
        class FooBar(object):
            pass
        arr = np.arange(30)
        assert_raises(TypeError, pad, arr, FooBar())

    def test_complex(self):
        arr = np.arange(30)
        assert_raises(TypeError, pad, arr, complex(1, -1))
        assert_raises(TypeError, pad, arr, np.array(complex(1, -1)))

    def test_check_wrong_pad_amount(self):
        arr = np.arange(30)
        arr = np.reshape(arr, (6, 5))
        kwargs = dict(mode='mean', stat_length=(3, ))
        assert_raises(TypeError, pad, arr, ((2, 3, 4), (3, 2)),
                      **kwargs)
