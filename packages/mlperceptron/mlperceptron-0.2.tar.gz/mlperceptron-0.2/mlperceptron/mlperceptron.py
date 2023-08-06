import numpy as np
from scipy import optimize


class NeuralNetwork(object):
    """Building N layers neural network (1 input, N hidden, and 1 output).
       Default has one 25 units hidden layer.
    """

    def __init__(self, hidden_layers=(25,)):
        """Initialize Neural Network.

        Args:
            hidden_layers (tuple): tuple of hidden layer(s) units.
        """
        self._hidden_layers = hidden_layers

    def _one_hot_encoder(self, y):
        """Change y (Nx1) binary matrix to (NxM) binary matrix.

        For example for 2 classes:
            y = [0;1;2;1]  # 4x1
        Becomes:
            y = [1 0 0;0 1 0; 0 0 1;0 1 0]  # 4x3

        The following does the same thing:
            from sklearn.preprocessing import OneHotEncoder
            encoder = OneHotEncoder(sparse=False)
            encoder.fit_transform(y)
        But if I use sklearn, I can use their MLP class.
        So, that is not cool.

        Args:
            y (np.matrix): Nx1 matrix for targets.
        Returns:
            np.matrix: NxM binary matrix.
        """
        num_labels = len(set([int(i) for i in y]))
        return np.eye(num_labels)[y]

    def _get_optimal_epsilon(self, lin, lout):
        """Get optimal eplison value.

        Args:
            lin (int): no. of units in layer s.
            lout (int): no. of units in layer s+1.
        Returns:
            float: eplison.
        """
        return np.sqrt(6) / np.sqrt(lin + lout)

    def _sigmoid(self, x):
        """Logistic activation function."""
        return 1.0 / (1.0 + np.exp(-x))

    def _sigmoid_gradient(self, z):
        """Derivative of logistic activation function."""
        return np.multiply(self._sigmoid(z), (1 - self._sigmoid(z)))

    def _flatten_thetas(self, thetas):
        """Flatten thetas.

        Flatten tetas into 1D array for feeding into scipy minimize method.

        Args:
            thetas (list): list of thetas matrices.
        Returns:
            np.matrix: 1XN matrix.
        """
        flattened_thetas = []
        for theta in thetas:
            flattened_thetas.append(np.ravel(theta))
        return np.hstack(tuple(flattened_thetas))

    def _unflatten_thetas(self, flattened_thetas, thetas_shapes):
        """Unflatten thetas.

        Retrive back list of thetas from a 1D array from scipy
        minimize method.

        Args:
            flattened_thetas (list): array of weights.
            thetas_shapes (list): list of tuples which are the shapes of
                each theta matrix.
        Returns:
            list: list of thetas numpy matrices.
        """

        flattened_thetas = np.array(flattened_thetas)
        thetas = []
        current_index = 0
        for shape in thetas_shapes:
            row, col = shape
            theta = np.matrix(
                flattened_thetas[
                current_index:row * col + current_index]).reshape(row, col)
            thetas.append(theta)
            current_index += row * col
        return thetas

    def _initialize_thetas(self, X, y):
        """Build matrices of weights randomly.

        Args:
            X (np.matrix): NxN matrix of taining data.
            y (np.matrix): Nx1 matrix for targets.
        Returns:
            list: list of thetas matrices.
        """

        thetas = []
        num_labels = len(set([int(i) for i in y]))
        input_layer_units, output_layer_units = X.shape[1], num_labels
        last_layer_units = input_layer_units
        for index, hidden_layer_units in enumerate(self._hidden_layers):
            ep = self._get_optimal_epsilon(
                last_layer_units, hidden_layer_units)
            thetas.append(np.random.rand(
                hidden_layer_units, last_layer_units + 1) * 2.0 * ep - ep)
            last_layer_units = hidden_layer_units
        ep = self._get_optimal_epsilon(last_layer_units, output_layer_units)
        thetas.append(np.random.rand(
            output_layer_units, hidden_layer_units + 1) * 2.0 * ep - ep)
        return thetas

    def _cost(self, y, h, m):
        """Compute error.

        Args:
            y (np.matrix): Nx1 matrix for targets.
            h (np.matrix): result matrix from hypothesis function.
            m (int): rows of training data.
        Returns:
            float: error.
        """
        if m == 0:
            raise Exception('No training data found.')
        J = 0
        for i in range(m):
            first_term = np.multiply(-y[i, :], np.log(h[i, :]))
            second_term = np.multiply((1 - y[i, :]), np.log(1 - h[i, :]))
            J += np.sum(first_term - second_term)
        return J / m

    def _regularization(self, J, thetas, lambd, m):
        """Adjust error by adding regularization term.

        Args:
            J (float): error computed from result hypothesis matrix.
            thetas (list): list of numpy matrices of weights.
            m (int): rows of training data.
        Returns:
            float: adjusted error.
        """
        return J + np.sum([np.sum(np.power(theta[:, 1:], 2)) for theta in thetas]) * lambd / (2.0 * m)

    def _feedforward_pass(self, X, thetas):
        """Perform forward pass.

        Args:
            X (np.matrix): training data.
            thetas (list): list of numpy matrices of weights.
        Returns:
            tuple: tuple that contains a_s, z_s and h where
                a_s is the result after applying activation function,
                z_s is dot product of weights and last result of activation
                function and h is the final result matrix from hypothesis
                function.
        """
        a_s = []
        z_s = []
        m = X.shape[0]
        for i, theta in enumerate(thetas):
            if i == 0:
                tmp_a = np.insert(X, 0, values=np.ones(m), axis=1)
            else:
                tmp_a = np.insert(
                    self._sigmoid(z_s[-1]), 0, values=np.ones(m), axis=1)
            a_s.append(tmp_a)
            z = tmp_a * theta.T
            z_s.append(z)
        h = self._sigmoid(z_s[-1])
        return a_s, z_s, h

    def _get_cost_and_gradient(
            self, flatten_thetas, lambd, X, y, shapes, show_cost=False):
        """Get cost and gradient for feeding into scipy library.

        Scipy library will call this repeatedly to minimize the gradient,
        decrease the cost (error).

        Args:
            flatten_thetas (np.matrix): 1XN numpy matrices of thetas.
            lambd (float): lambda value for regularization.
            X (np.matrix): training data.
            y (np.matrix): targets.
            shapes (list): list of tuples of shapes of the thetas.
            show_cost (boolean): True if you want to see the change
                of cost for each iteration.
        Returns:
            tuple: tuple of a float and an 1XN numpy matrix for the
                cost and the gradient.
        """
        thetas = self._unflatten_thetas(flatten_thetas, shapes)
        m = X.shape[0]
        X = np.matrix(X)
        y = np.matrix(y)
        y = np.matrix(self._one_hot_encoder(y))
        a_s, z_s, h = self._feedforward_pass(X, thetas)
        gradient = [np.zeros(theta.shape) for theta in thetas]
        z_s.pop()
        for t in range(m):
            yt = y[t, :]
            ht = h[t, :]
            dLt = ht - yt
            deltas = [dLt]
            last_delta = dLt
            for i in range(0, len(self._hidden_layers)):
                zt = z_s[-1 - i][t, :]
                zt = np.insert(zt, 0, values=np.ones(1))
                dt = np.multiply(
                    last_delta * thetas[-1 - i], self._sigmoid_gradient(zt))
                last_delta = dt[:, 1:]  # Remove bias from all deltas besides the last delta.
                deltas.append(last_delta)
            for i, a in enumerate(a_s):
                gradient[i] = gradient[i] + deltas[-1 - i].T * a[t, :]

        for i, d in enumerate(gradient):
            gradient[i] = gradient[i] / m
            gradient[i][:, 1:] = gradient[i][:, 1:] + (thetas[i][:, 1:] * lambd) / m

        J = self._cost(y, h, m)
        if lambd != 0:
            J = self._regularization(J, thetas, lambd, m)
        if show_cost:
            print('Loss: {}'.format(J))
        return J, self._flatten_thetas(gradient)

    def train(self, X, y, lambd, maxiter=200, show_cost=False):
        """Perform data training.

        Args:
            X (np.matrix): training data.
            y (np.matrix): targets.
            lambd (float): lambda value for regularization.
            maxiter (int): maximum iteration for scipy minimize.
            show_cost (boolean): True if you want to see change of
                cost for each iteration.
        Returns:
            list: list of weights in form of numpy matrices.
        """
        thetas = self._initialize_thetas(X, y)
        thetas_shapes = [m.shape for m in thetas]

        x0 = self._flatten_thetas(thetas)
        fmin = optimize.minimize(
            fun=self._get_cost_and_gradient, x0=x0,
            jac=True,
            method='TNC',
            args=(lambd, X, y, thetas_shapes, show_cost),
            options={'maxiter': maxiter})
        return self._unflatten_thetas(fmin.x, thetas_shapes)

    def predict(self, X, thetas):
        """Predict

        Perform feed forward with the optimal weights to predict things.

        Args:
            X (np.matrix): training data.
            thetas (list): list of optimal weights in form of numpy matrices.
        """
        a_s, z_s, h = self._feedforward_pass(X, thetas)
        return np.array(np.argmax(h, axis=1))

    def accuracy(self, y_pred, expected):
        """Print accuracy (%) be comparing predicted value and actual values.

        Args:
            y_pred (np.matrix): Nx1 predicted value matrix.
            expected (np.matrix): Nx1 predicted value matrix.
        """
        correct = [1 if a == b else 0 for (a, b) in zip(y_pred, expected)]
        accuracy = (sum(map(int, correct)) / float(len(correct)))
        return accuracy
