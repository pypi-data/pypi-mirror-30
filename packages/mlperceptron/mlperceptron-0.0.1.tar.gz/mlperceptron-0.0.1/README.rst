| |Build Status|

Multilayer Perceptron in Python
-----------------------------------

Python implementation of multilayer perceptron neural network from scratch.

    | Minimal neural network class with regularization using scipy minimize. Contains clear pydoc for learners to better understand each stage in the neural network.
    | https://github.com/paulokuong/neural_network

Requirements
------------

-  Python 3.4 (tested)

Goal
----

| To provide an example of a simple MLP for educational purpose.

Code sample
-----------

| Predicting outcome of AND logic gate:

X = 000, 001, 010, 011, 100, 101, 110, 111
    y = 0,0,0,0,0,0,1

    Data we want to predict:
    p = 011, 111, 000, 010, 111
    Expected results are: 0, 1, 0, 0, 1

.. code:: python

    import numpy as np
    from mlperceptron.mlperceptron import NeuralNetwork

    X = np.matrix(
        '0 0 0;0 0 1;0 1 0;0 1 1;1 0 0;1 0 1;1 1 0;1 1 1')
    y = np.matrix('0;0;0;0;0;0;0;1')
    n = NeuralNetwork((5,5,))

    g = n.train(X, y, 0.01, show_cost=True)
    y_pred = n.predict(np.matrix('0 1 1;1 1 1;0 0 0;0 1 0;1 1 1'), g)

    print(y_pred)
    print(n.accuracy(y_pred, np.matrix('0;1;0;0;1')))


Contributors
------------

-  Paulo Kuong (`@pkuong`_)

.. _@pkuong: https://github.com/paulokuong

.. |Build Status| image:: https://travis-ci.org/paulokuong/neural_network.svg?branch=master
.. target: https://travis-ci.org/paulokuong/neural_network
