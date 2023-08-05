"""Estimator module for Mutual Information."""
from __future__ import division, print_function

import numpy as np
import scipy.optimize
import sys

from scipy.special import gamma as gammaf
from sklearn.base import BaseEstimator
from sklearn.neighbors import NearestNeighbors
from sklearn.utils.multiclass import type_of_target

from midas.utils.sample_generation import marginal_distributions
from midas.utils.parameters_estimation import empirical_copula
from midas.utils.parameters_estimation import volume_of_the_unit_ball
from midas.utils.parameters_estimation import compute_gamma, sum_p_power


def mi_estimator_gamma(X, alpha=.99, k=3, gamma=-1., mtype='r', method='knn',
                       normalise=False, unbiased=True):
    """Estimation of Renyi or Tsallis Mutual information through entropy.

    This formula requires the computation of gamma. For further information,
    see Pal et al. (2010)
    http://david.palenica.com/papers/nn/Renyi-rates-NIPS-camera-ready-final.pdf

    Parameters
    ----------
    X : array_like
        DxN matrix of N i.i.d samples for D random variables.
    alpha : float
        Coefficient for the Renyi mutual information.
    k : int
        Number of neighbours to consider in the computation of Renyi MI.
    gamma : float
        Constant. Estimated from the function 'compute_gamma'.
    mtype : string
        Values:
        'r', 'renyi' - Renyi Mutual Information estimation
        't', 'tsallis' - Tsallis Mutual Information estimation
    method : string
        'knn' of 'kth' method. 'knn' has been shown to improve convergence rate
        as shown in Pal et al. (2010).
    normalise : bool, optional
        Normalise the mutual information value by sqrt(d), so that the
        mutual information between variables with different dimensions is more
        comparable.

    Returns
    -------
    mi : float
        Value of the estimated mutual information.

    """
    # determine number of sample n and number of variables d
    d, n = X.shape

    # Compute gamma if not specified
    if gamma < 0:
        gamma = compute_gamma(d=d, k=k, alpha=alpha, n=n, method=method)

    if unbiased:
        gamma *= (gammaf(k-alpha+1) * gammaf(k+alpha-1)) / gammaf(k) ** 2

    # Empirical copula transformation
    # print('renyiMI: copula transformation...')
    Z = empirical_copula(X)

    del X  # save memory if X is very big

    Z = Z.T  # NN method wants NxD matrix
    # Computes the generalized kNN graph. For high dimensional problem,
    # algorithm='ball_tree' works better, even if slower
    knn_alg = 'ball_tree' if d > 5 else 'auto'

    # print('renyiMI: g-knn ...')
    nbrs = NearestNeighbors(n_neighbors=k+1, algorithm=knn_alg).fit(Z)
    Z = nbrs.kneighbors(Z)[0]

    # Compute Lp(Xn): the sum of the p-th powers of Euclidean lengths of
    # generalized kNN edges
    if method == 'kth':
        Z = Z[:, k]

    Lp = sum_p_power(Z, d*(1.-alpha))

    tmp = 0.
    if mtype[0] == 'r':
        # Renyi MI estimation
        tmp = np.log(Lp) - (np.log(gamma) + alpha * np.log(n))
    elif mtype[0] == 't':
        # Tsallis MI estimation
        tmp = Lp / (gamma * n ** alpha) - 1.
    else:
        raise Exception('Method unsupported: %s' % mtype)

    mi = tmp / (alpha - 1.)

    if normalise:
        mi /= np.sqrt(d)

    return mi


def compute_weights(n_dim, n_samples, k):
    """Compute weights for the weighted mutual information estimator."""
    winit = np.ones(k, np.float) / k  # initial guess of weights
    eps = np.sqrt(1. / n_samples)  # epslon value
    ub = 10 * winit[0]  # upper boound for each value
    lb = -ub  # lower bound

    cons_list = [{'type': 'eq', 'fun': (lambda x: sum(x) - 1)}]

    def f(x, l, i, n_dim):
        return x * (l ** (i / n_dim))

    r = range(1, k + 1)
    for i in r:
        cons_list.append({'type': 'ineq',
                          'fun': lambda x: eps -
                          abs(sum(map(f, x, r, [i] * k, [n_dim] * k)) *
                              n_samples ** (-i / n_dim))})
    cons = tuple(cons_list)
    bnds = tuple([(lb, ub)] * k)
    res = scipy.optimize.minimize(
        lambda x: np.linalg.norm(x, ord=1),
        winit, method='SLSQP', bounds=bnds, constraints=cons)
    return res.x


class RenyiMutualInformationEntropy(BaseEstimator):
    """Estimation of Renyi mutual information of X with an alternative
    formula for the entropy computation that does not require gamma.

    See Leonenko (2008) - http://core.ac.uk/download/pdf/22087.pdf (3.13,
    3.14). In this case gamma is not required because it is considered the
    kth case.

    Parameters
    ----------
    alpha : float, optional, default 0.99
        Coefficient for the Renyi mutual information.
    k : int, optional, default 3
        Number of neighbours to consider in the computation of kNN.
    copula : bool, optional, default False
        Transform input points through empirical copula.
    normalize : bool, optional, default False
        Normalise the mutual information value by sqrt(d), so that the
        mutual information between variables with different dimensions is more
        comparable.
    allow_negative : bool, optional, default True
        Cut negative values to zero.
    """
    _estimator_type = "classifier"

    def __init__(self, alpha=0.99, k=3, gamma=None, n_iter=10, copula=False,
                 normalize=False, allow_negative=False):
        self.alpha = alpha
        self.k = k
        self.gamma = gamma
        self.n_iter = n_iter
        self.copula = copula
        self.normalize = normalize
        self.allow_negative = allow_negative

    def fit(self, X, y=None):
        """Fit the model.

        Parameters
        ----------
        X : array-like, 2-dimensional
            NxD matrix of N i.i.d samples for D-dimensional random variables.
        y : array-like, optional, default None
            Unused label vector. Present only for compatibility.
        """
        n_samples, n_dim = X.shape

        # Copula estimation. The copula transformation step is guaranteed by a
        # property of mutual information (rescaling property), which states that
        # arbitrary strictly increasing functions applied to the argument
        # do not change the multi information value
        Z = empirical_copula(X)

        distZ = NearestNeighbors(
            n_neighbors=self.k + 1, algorithm='ball_tree').fit(Z).kneighbors(
                Z)[0]

        volume_unit_ball_alpha = volume_of_the_unit_ball(
            n_dim) ** (1 - self.alpha)

        # C = (gammaf(k)/gammaf(k+1.-alpha))**(1./(1.-alpha))
        cs = gammaf(self.k) / gammaf(self.k + 1 - self.alpha)
        cs *= np.sum(distZ[:, self.k] ** (n_dim * (1 - self.alpha)))

        I_alpha = (n_samples - 1.) / n_samples * volume_unit_ball_alpha * cs \
            / (n_samples - 1.) ** self.alpha
        H = np.log(I_alpha) / (1. - self.alpha)

        if self.normalise:
            H /= np.sqrt(n_dim)
        self.rmi_ = -H

        return self


class RenyiMutualInformationDivergence(BaseEstimator):
    """Estimation of Renyi mutual information of X with a divergence estimator.

    See Eq. (7) in http://arxiv.org/abs/1202.3758
    Renyi mutual information is defined as the divergence between the joint
    variables distribution and the marginal variable distributions.
    The use of the copula is optional, but in higher
    dimension the value of rmi is over estimated (the error is more or less the
    same). This can also slower the method, but reduces the standard deviation
    of the results. Multi-information values are overestimated.
    See 'robustness and detection limit' results.

    Parameters
    ----------
    alpha : float, optional, default 0.99
        Coefficient for the Renyi mutual information.
    k : int, optional, default 3
        Number of neighbours to consider in the computation of kNN.
    copula : bool, optional, default False
        Transform input points through empirical copula.
    normalize : bool, optional, default False
        Normalise the mutual information value by sqrt(d), so that the
        mutual information between variables with different dimensions is more
        comparable.
    allow_negative : bool, optional, default True
        Cut negative values to zero.
    """
    _estimator_type = "classifier"

    def __init__(self, alpha=0.99, k=3, gamma=None, n_iter=10, copula=False,
                 normalize=False, allow_negative=False):
        self.alpha = alpha
        self.k = k
        self.gamma = gamma
        self.n_iter = n_iter
        self.copula = copula
        self.normalize = normalize
        self.allow_negative = allow_negative

    def max_mutual_information(self, n_dim, n_samples=100, n_iter=10):
        X = np.random.multivariate_normal(
            np.zeros(n_dim), np.ones((n_dim, n_dim)) + np.eye(n_dim) * 0.1,
            n_samples)
        normalize_copy = self.normalize
        self.normalize = False
        mi = np.sum(self._fit(X) for _ in range(n_iter)) / float(n_iter)
        self.normalize = normalize_copy

        return mi

    def _fit(self, X, y=None, marginals=None):
        """Fit the model using divergences.

        Parameters
        ----------
        X : array-like, 2-dimensional
            NxD matrix of N i.i.d samples for D-dimensional random variables.
        y : array-like, optional, default None
            Unused label vector. Present only for compatibility.

        Returns
        -------
        rmi : float
            Value of the estimated Renyi mutual information.
        """
        n_samples, n_dim = X.shape

        # The Renyi Mutual Information is defined as the divergence between
        # the joint probability and the marginal variables.

        if self.copula:
            # empirical copula transformation
            X = empirical_copula(X)
            # Y = est.empirical_copula(Y)
            # marginals of copula are uniforms
            marginals = np.random.uniform(size=(n_samples, n_dim))
        elif marginals is None:
            # Simulate the marginal variables
            marginals = marginal_distributions(X)

        # Compute the generalized kNN graph
        nbrs = NearestNeighbors(
            n_neighbors=self.k + 1, algorithm='ball_tree').fit(X)
        distX = nbrs.kneighbors(X)[0]
        distX = distX[:, self.k]  # kth nearest neighbor

        nbrs = NearestNeighbors(
            n_neighbors=self.k, algorithm='ball_tree').fit(marginals)
        distY = nbrs.kneighbors(X)[0]
        distY = distY[:, self.k - 1]  # kth nearest neighbor

        # B: correction term for an unbiased estimator
        gammaf_k = gammaf(self.k)
        B = gammaf_k * gammaf_k / (
            gammaf(self.k - self.alpha + 1) * gammaf(self.k + self.alpha - 1))
        # B = 1. * gammaf(k) * gammaf(k+2.-2.*alpha) / (gammaf(k-alpha+1) ** 2)

        # Divergence estimation
        if np.min(distY) == 0:
            distX += .01
            distY += .01
        s = np.mean((
            (n_samples - 1) / n_samples * (distX / distY) ** n_dim) ** (
                1 - self.alpha)) * B
        # if isnan(s) or (s <= 0 and mtype[0] == 'r'):
        if np.isnan(s) or s <= 0:  # avoid -inf and nan results
            raise ValueError("Divergence estimation produced NaN or negative "
                             "results.")

        # tmp = 0.
        # if mtype[0] == 'r':
        #     # Renyi MI estimation
        #     tmp = log(s)
        # elif mtype[0] == 't':
        #     # Tsallis MI estimation
        #     tmp = s - 1.
        # mi = tmp / (alpha - 1.)
        mi = np.log(s) / (self.alpha - 1.)

        if not self.allow_negative and mi < 0:
            mi = 0
        elif self.normalize:
            # mi /= np.sqrt(n_dim)
            norm_by = self.max_mutual_information(n_dim, n_samples=n_samples)
            if norm_by != 0:
                mi /= norm_by
        return mi

    def fit(self, X, y=None, marginals=None):
        """n_iter added."""
        self.rmi_ = np.mean([self._fit(X, y, marginals=marginals)
                             for i in range(self.n_iter)])
        return self


class RenyiMutualInformationWeighted(BaseEstimator):
    """Estimation of Renyi mutual information with a weighted estimator.

    See http://ieeexplore.ieee.org/ielx5/5959910/5967628/05967818.pdf?tp=&arnumber=5967818&isnumber=5967628,
    Sricharan and Hero, "Weighted k-NN graphs for Renyi entropy estimation in
    high dimensions"

    Parameters
    ----------
    alpha : float, optional, default 0.99
        Coefficient for the Renyi mutual information.
    k : int, optional, default 3
        Number of neighbours to consider in the computation of kNN.
    n_iter : int, optional, deafult 10,
        Increase the stability of the estimator.
    copula : bool, optional, default False
        Transform input points through empirical copula.
    normalize : bool, optional, default False
        Normalise the mutual information value by sqrt(d), so that the
        mutual information between variables with different dimensions is more
        comparable.
    allow_negative : bool, optional, default True
        Cut negative values to zero.
    """
    _estimator_type = "classifier"

    def __init__(self, alpha=0.99, k=3, n_iter=10, copula=False,
                 normalize=False, allow_negative=True, verbose=0):
        self.alpha = alpha
        self.k = k
        self.n_iter = n_iter
        self.copula = copula
        self.normalize = normalize
        self.allow_negative = allow_negative
        self.verbose = verbose

    def fit(self, X, y=None):
        """Fit the model using divergences.

        Parameters
        ----------
        X : array-like, 2-dimensional
            NxD matrix of N i.i.d samples for D-dimensional random variables.
        y : array-like, optional, default None
            Unused label vector. Present only for compatibility.

        Returns
        -------
        rmi : float
            Value of the estimated Renyi mutual information.
        """
        n_samples, n_dim = X.shape

        rmi_ = 0.
        for i in range(self.n_iter):
            if self.verbose:
                print("Starting iter (%02d/%02d)" % (i, self.n_iter),
                      file=sys.stderr)
            sum_product = 0
            weights = compute_weights(n_dim, n_samples, self.k)
            marginals = marginal_distributions(X)
            for k in range(self.k):
                mi_score_k = RenyiMutualInformationDivergence(
                    alpha=self.alpha, k=k + 1, n_iter=self.n_iter,
                    copula=self.copula, normalize=self.normalize,
                    allow_negative=self.allow_negative).fit(
                        X, marginals=marginals).rmi_
                sum_product += mi_score_k * weights[k]
            rmi_ += sum_product

        self.rmi_ = rmi_ / self.n_iter

        return self


class MIDAS(BaseEstimator):
    _estimator_type = "classifier"

    def __init__(self, estimator=None, group=None):
        self.estimator = estimator
        self.group = group

    def fit(self, X, y):
        X_group = X[:, self.group] if self.group is not None else X

        if type_of_target(y) != 'binary':
            raise ValueError("Only binary label vectors supported. `y` was "
                             "found of type %s" % type_of_target(y))

        class_0, class_1 = np.unique(y)
        rmi_0 = self.estimator.fit(X_group[y == class_0]).rmi_
        rmi_1 = self.estimator.fit(X_group[y == class_1]).rmi_

        self.dmi_ = np.abs(rmi_1 - rmi_0)

        return self

    def score(self, X, y):
        # X_group = X[:, self.group] if self.group is not None else X
        #
        # # XXX let's assume y is binary classification.
        # # TODO check if it is true
        #
        # class_0, class_1 = np.unique(y)
        # rmi_0 = self.estimator.fit(X_group[y == class_0]).rmi_
        # rmi_1 = self.estimator.fit(X_group[y == class_1]).rmi_
        #
        # dmi_ = np.abs(rmi_1 - rmi_0)
        #
        # return -abs(self.dmi_ - dmi_) + 1
        return self.dmi_
