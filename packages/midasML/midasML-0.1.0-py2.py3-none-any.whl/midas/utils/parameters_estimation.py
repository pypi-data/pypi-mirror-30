#!/usr/bin/env python
"""Functions to estimate parameters involved in the computation of mutual
information.

Import this file as
    import utils.parameters_estimation as est

@author: Federico Tomasi
@email:  fdtomasi@gmail.com
"""
from __future__ import division
import numpy as np
import scipy.stats as ss

from numpy import pi, sum as npsum, zeros, eye
from numpy.random import multivariate_normal as mvnrnd
from scipy.stats import rankdata
from scipy.special import gamma as gammaf
from sklearn.neighbors import NearestNeighbors

# from . import sample_generation as sg


def volume_of_the_unit_ball(d):
    """Volume of the d-dimensional unit ball.

    See http://en.wikipedia.org/wiki/Volume_of_an_n-ball and
    http://core.ac.uk/download/pdf/22087.pdf

    Parameters
    ----------
    d : int
        Dimensions.

    Returns
    -------
    v : float
        Volume of the d-dimensional unit ball.
    """
    return pi**(d/2.) / gammaf(d/2.+1)


def sum_p_power(X, p):
    """Compute the sum of the p-th powers of Euclidean lengths of
    generalized kNN edges in the matrix X.
    """
    return npsum(npsum(X ** p))


def compute_gamma(d=3, k=3, alpha=.99, n=4000., method='knn'):
    r"""Analytical estimation of gamma as pointed out by Dougal.

    gamma = $\sum_{j \in S} gamma_j$
    See Eq. (295) in ITE documentation.

    Parameters
    ----------
    d : int
        Number of dimensions of each variable.
    k : int
        Number of neighbours to consider for each random variable.
    alpha : float
        Parameter of multi information estimation.
    n : int
        Number of i.i.d. sample (n -> inf)
    method : string
        'knn' or 'kth' in the computation of NN edges.

    Returns
    -------
    gamma : float
        gamma = $\sum_{j \in S} gamma_j$
        For the formula of gamma_j see Eq. (294) in ITE documentation.
    """
    S = []
    if method == 'knn':
        S = range(1, k+1)
    elif method == 'kth':
        S = [k]
    else:
        raise Exception('Method {} unknown'.format(method))

    V = volume_of_the_unit_ball(d)
    s = 0.
    for j in S:
        s = s + gammaf(j+1.-alpha) / gammaf(j)
    # s = np.sum([((n-1.)/n*V) ** (alpha-1.) * gammaf(j+1.-alpha) / gammaf(j) for j in S])
    # for n -> inf, c -> 1
    c = (n-1.)/n
    return (c*V) ** (alpha-1.) * s


def compute_gamma_emp(d, k, alpha, n):
    """[Deprecated.]

    Empirical estimation of lim Lp(X1:n)/n^(1-p/d) = gamma
    with knn distances.

    As recently pointed out by Dougal
    (see "https://bitbucket.org/szzoli/ite/issue/5/hrenyi_knn-constant-has-a-closed-form")
    this is a bit superfluous and computationally really expensive.
    See Eq. (295) in ITE documentation and 'compute_gamma' function for another
    estimator.

    Parameters
    ----------
    d : int
        Number of dimensions of each variable.
    k : int
        Number of neighbours to consider for each random variable.
    alpha : float
        Parameter of multi information estimation.
    n : int
        Number of i.i.d. sample to generate in order to compute gamma.

    Returns
    -------
    gamma : float
        Empirical estimation of lim Lp(X1:n)/n^(1-p/d).
    """
    # Generation of the i.i.d. sample from the uniform distribution over the
    # d-dimensional cube [0,1]^d
    # print('compute_gamma: gaussian copula ...')
    X = mvnrnd(zeros(d), eye(d), n)
    X = ss.norm.cdf(X, 0, 1)
    X = ss.uniform.ppf(X, 0, 1)

    # Computes the generalized kNN graph
    # print('compute_gamma: knn ...')
    nbrs = NearestNeighbors(n_neighbors=k+1).fit(X)
    X, _ = nbrs.kneighbors(X)

    # Compute Lp(Xn): the sum of the p-th powers of Euclidean lengths of
    # generalized kNN edges
    Lp = sum_p_power(X, d*(1.-alpha))

    # Empirical estimation of gamma
    gamma = 1. * Lp / n ** alpha
    return gamma


def quantile_disc(values, nbin):
    """Quantile discretisation of a vector in nbin parts."""
    if values.shape[0] < 2:
        raise Exception('Values shape incorrect.')

    v_disc = (np.ceil(nbin * rankdata(values) / values.shape[0])) - 1

    '''pivots = np.zeros((nbin, 1))
    for i in range(nbin):
        l = values[v_disc == i]
        pivots[i] = 0 if len(l) == 0 else np.max(l)
    '''
    pivots = []
    return pivots, v_disc


def rank_transform(X):
    """Rank transformation of a D times N matrix X.

    If two values are equal, the ordinal rank is returned,
    since the copula transformation must be a stricly increasing function
    to preserve the rescaling property off mutual information.

    Parameters
    ----------
    X : array
        (Multi-dimensional) array to transform, DxN.

    Returns
    -------
    Z : array
        Ranked (multi-dimensional) array, DxN.
    """
    d, n = X.shape
    Z = zeros((d, n))
    for i in xrange(d):
        Z[i, :] = 1. * rankdata(X[i, :], method='max')
    return Z


def empirical_copula(X):
    """Empirical copula transformation.

    Parameters
    ----------
    X : array
        (Multi-dimensional) array to transform, NxD.

    Returns
    -------
    Z : array
        Ranked (multi-dimensional) array, NxD.
    """
    n_samples, n_dim = X.shape
    Z = zeros((n_samples, n_dim))
    for i in xrange(n_dim):
        Z[:, i] = 1. * rankdata(X[:, i], method='max')
    return Z / n_samples
