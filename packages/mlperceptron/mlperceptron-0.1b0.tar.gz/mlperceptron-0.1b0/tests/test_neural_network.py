from __future__ import absolute_import
from __future__ import print_function
from unittest.mock import patch
from neural_network import NeuralNetwork
import pytest
import numpy as np

try:
    from unittest.mock import MagicMock
except:
    from mock import MagicMock


def test_get_optimal_epsilon():
    n = NeuralNetwork((2,))
    assert n._get_optimal_epsilon(2, 2) == 1.2247448713915889


def test_sigmoid():
    n = NeuralNetwork((2,))
    m = np.matrix(
        '0.73105858 0.88079708; '
        '0.95257413 0.98201379; '
        '0.99330715,  0.99752738').round(5)
    actual = n._sigmoid(np.matrix('1 2; 3 4; 5 6')).round(5)
    np.testing.assert_array_equal(m, actual)


def test_sigmoid_gradient():
    n = NeuralNetwork((2,))
    m = np.matrix(
        '0.19661193 0.10499359;'
        '0.04517666 0.01766271;'
        '0.00664806 0.00246651').round(5)
    actual = n._sigmoid_gradient(np.matrix('1 2; 3 4; 5 6')).round(5)
    np.testing.assert_array_equal(m, actual)


def test_initialize_thetas():
    """
    [(50, 4), (50, 51), (50, 51), (2, 51)]
    """
    X = np.matrix(
        '0 0 0;0 0 1;0 1 0;0 1 1;1 0 0;1 0 1;1 1 0;1 1 1')
    y = np.matrix('0;0;0;0;0;0;0;1')
    n = NeuralNetwork((50, 50, 50,))
    actual = n._initialize_thetas(X, y)
    assert len(actual) == 4
    assert actual[0].shape == (50, 4)
    assert actual[1].shape == (50, 51)
    assert actual[2].shape == (50, 51)
    assert actual[3].shape == (2, 51)


def test_feedforward_pass():
    X = np.matrix(
        '0 0 0;0 0 1;0 1 0;0 1 1;1 0 0;1 0 1;1 1 0;1 1 1')
    y = np.matrix('0;0;0;0;0;0;0;1')
    n = NeuralNetwork((2, 2,))
    thetas = n._initialize_thetas(X, y)
    actual = n._feedforward_pass(X, thetas)
    m = X.shape[0]

    a1 = np.insert(X, 0, values=np.ones(m), axis=1)
    z1 = a1 * thetas[0].T
    a2 = np.insert(
        n._sigmoid(z1), 0, values=np.ones(m), axis=1)
    z2 = a2 * thetas[1].T
    a3 = np.insert(
        n._sigmoid(z2), 0, values=np.ones(m), axis=1)
    z3 = a3 * thetas[2].T
    expected_h_theta = n._sigmoid(z3)

    np.testing.assert_array_equal(actual[0][0], a1)
    np.testing.assert_array_equal(actual[0][1], a2)
    np.testing.assert_array_equal(actual[0][2], a3)
    np.testing.assert_array_equal(actual[1][0], z1)
    np.testing.assert_array_equal(actual[1][1], z2)
    np.testing.assert_array_equal(actual[1][2], z3)
    np.testing.assert_array_equal(actual[2], expected_h_theta)


def test_cost():
    n = NeuralNetwork((2,))
    X = np.matrix('1 2; 3 4; 5 6')
    y = np.matrix('1;0;1')
    m = X.shape[0]
    thetas = [
        np.matrix(
            '-0.73947824 -0.65373806 0.52660202;'
            '0.07059914 0.6765674 1.04742516'),
        np.matrix(
            '0.83236978 -0.15422844 -1.20198309;'
            '-0.84706711 -0.10041546 0.96957002')
    ]
    a_s, z_s, h_theta = n._feedforward_pass(X, thetas)
    actual = n._cost(y, h_theta, m)
    assert round(actual, 6) == 1.461498


def test_regularization():
    n = NeuralNetwork((2,))
    X = np.matrix('1 2; 3 4; 5 6')
    y = np.matrix('1;0;1')
    m = X.shape[0]
    lambd = 1
    thetas = [
        np.matrix(
            '-0.73947824 -0.65373806 0.52660202;'
            '0.07059914 0.6765674 1.04742516'),
        np.matrix(
            '0.83236978 -0.15422844 -1.20198309;'
            '-0.84706711 -0.10041546 0.96957002')
    ]
    a_s, z_s, h_theta = n._feedforward_pass(X, thetas)
    J = n._cost(y, h_theta, m)
    actual = n._regularization(J, thetas, lambd, m)
    assert round(actual, 6) == 2.241202


def test_get_cost_and_gradient():
    n = NeuralNetwork((2,))
    X = np.matrix('1 2; 3 4; 5 6')
    y = np.matrix('1;0;1')
    m = X.shape[0]
    lambd = 1
    thetas = [
        np.matrix(
            '-0.73947824 -0.65373806 0.52660202;'
            '0.07059914 0.6765674 1.04742516'),
        np.matrix(
            '0.83236978 -0.15422844 -1.20198309;'
            '-0.84706711 -0.10041546 0.96957002')
    ]
    J, gradient = n._get_cost_and_gradient(
        n._flatten_thetas(thetas), lambd, X, y, [(2, 3), (2, 3)])

    assert J == 2.120852393171714
    np.testing.assert_array_equal(
        np.matrix(gradient).round(4),
        np.matrix(
            ('0.0010795 -0.21435286 0.18017333 -0.01609168 '
             '0.21087382 0.3184014 0.06755033 -0.02659072 '
             '-0.3402597 -0.14962044 -0.08768394 0.18231439'
             '')).round(4))


def test_overall():
    X = np.matrix(
        '0 0 0;0 0 1;0 1 0;0 1 1;1 0 0;1 0 1;1 1 0;1 1 1')
    y = np.matrix('0;0;0;0;0;0;0;1')
    n = NeuralNetwork((50, 50, 50,))

    g = n.train(X, y, 0.01, show_cost=True)
    y_pred = n.predict(np.matrix('0 1 1;1 1 1;0 0 0;0 1 0;1 1 1'), g)

    assert n.accuracy(y_pred, [0, 1, 0, 0, 1]) > 0.96
