#!/usr/bin/env python
"""Routines for sample generation.

@author: Federico Tomasi
@email:  fdtomasi@gmail.com
"""
import numpy as np
import scipy.stats as stats


def marginal_distributions(X):
    """Generate samples of marginals from a joint distribution.

    Parameters
    ----------
    X : array-like
        Data matrix, n x d.
    """
    n_samples, n_dim = X.shape
    Y = np.zeros((n_samples, n_dim))
    a = np.arange(n_samples)
    for i in range(n_dim):
        np.random.shuffle(a)
        Y[:, i] = X[a, i]
    return Y


def lowrank_covariance(n_dim, n=1):
    """Generate a covariance matrix with Low Rank method.

    This is the probabilistic PCA or Factor analysis form.
    """
    w = np.random.multivariate_normal(np.zeros(n_dim), np.eye(n_dim), n).T
    return np.dot(w, w.T)


def sparseinverse_covariance(n_dim):
    """Generate a covariance matrix with Sparse Inverse method.

    Sparse graph where each element depends only on a subset of others.
    """
    # W is a weight symmetric matrix.
    # It has -1 if two vertices are connected, 0 otherwise.
    # The diagonal is the sum of rows (or columns).
    W = np.zeros((n_dim, n_dim))
    for i in range(n_dim):
        W[i, i + 1:] = np.random.randint(-1, 1, n_dim - i - 1)
    W += W.T
    w = [abs(np.sum(vec)) for vec in W]
    return np.linalg.inv(W + np.diag(w) + np.random.rand() ** 2 * np.eye(n_dim))


def random_vector(a, b, n):
    """Generate a vector of random values in [a,b)."""
    return a + (b - a) * np.random.rand(n)


def random_covariance(d, rho, a=.1, b=.5):
    """Generate a random covariance matrix with dependent variables.

    Returns
    -------
    covX : np.ndarray
        Dependent covariance matrix.
    """
    # Generate random sigma values
    sig = random_vector(a, b, d)
    covX = np.zeros((d, d))
    for i in range(d):
        covX[i, i] = sig[i] ** 2
        for j in range(i):
            covX[i, j] = covX[j, i] = rho * sig[i] * sig[j]

    # SigmaDep = SigmaDep + SigmaDep.T
    return covX


def betacopula(X, d, a=0., b=0.):
    """Transform multivariate normal distributions in Beta distribution.

    This is done via copula transformation.
    """
    if a == 0. and b == 0.:
        a, b = np.random.random(d), np.random.random(d)
    U = stats.norm.cdf(X, 0, 1)
    return stats.beta.ppf(U, a, b)


def genmvrs(d=3, n=1000, rho=.8, distr='gaussian'):
    """Random generation of multivariate random distribution.

    Through Gaussian Copula, it generates also multivariate Beta distributions.

    Parameters
    ----------
    d : int
        Number of dimensions of each variable.
    n : int
        Number of i.i.d samples.
    rho : float
        Correlation among variables. Values in [0, 1[
    alpha : float
        Parameter of multi information estimation.
    distr : 'gaussian', 'beta', 'rbf', 'exp', 'pol', 'cos', 'lin'
        Type of multivariate distribution. Apart from 'gaussian' and 'beta',
        the others require the python module GPy installed.

    Returns
    -------
    X : array
        d-by-n matrix (each column is a sample) produced by joint distribution.
    Y : array
        d-by-n matrix (each column is a sample) produced by marginal
        distribution.
    covX : array
        d-by-d matrix. Covariance matrix of X.
    """
    covX = []
    GPY_distributions = ('rbf', 'exp', 'pol', 'cos', 'lin')
    distr = distr.lower()
    if distr in GPY_distributions:
        # using GPy distributions
        from GPy import kern
        if distr == 'rbf':
            k = kern.RBF(2)
        elif distr == 'exp':
            k = kern.Exponential(2)
        elif distr == 'cos':
            k = kern.Cosine(2)
        elif distr == 'pol':
            k = kern.Poly(2)
        elif distr == 'lin':
            k = kern.Linear(2)
        covX = k.K(np.random.rand(d, n))
    else:
        # if distr is gaussian or beta, generate normal covariance matrices
        covX = random_covariance(d, rho)

    X = np.random.multivariate_normal(np.zeros(d), covX, n)
    Y = np.random.multivariate_normal(np.zeros(d), np.diag(np.diag(covX)), n)

    if distr == 'beta':
        # Use Gaussian Copula to produce Beta distributions
        X = betacopula(X, d)
        Y = betacopula(Y, d)

    # rmiX = renyi_i(covX, alpha)
    # - renyi_i(covY,alpha)  # the second term should be ~0
    # tmiX = tsallis_i(covX, np.diag(np.diag(X)), alpha)
    return X, Y, covX


def noisy_ds(ngep, ngens=760, ntrueM=50, rho=.8):
    """Generate a noisy dataset.

    Parameters:
    ----------
    ngep: number of GEPs in which genes are coexpressed
    ngens: total number of genes
    ntrueM: number of true modulators

    100 total GEPs
    """
    genes = range(ngens)  # sequence number for genes
    target = genes[:10]  # known target of the TF

    l = ngep
    mu = np.zeros(10)
    covX = random_covariance(10, rho)
    Xr = np.random.multivariate_normal(mu, covX, l)
    Xl = np.random.multivariate_normal(mu, np.diag(np.diag(covX)), 100-l)
    Xn = np.concatenate((Xl, Xr), axis=0)

    M = genes[10:]
    trueM_n = M[:ntrueM]
    falseM_n = M[ntrueM:-10]

    falseM = np.array([np.random.normal(scale=(.5*np.random.rand()), size=100)
                       for x in range(len(falseM_n))]).T

    trueMr = np.array([(np.random.normal(loc=1., scale=.1, size=50))
                       for x in range(len(trueM_n))]).T
    trueMl = np.array([(np.random.normal(loc=0., scale=.1, size=50))
                       for x in range(len(trueM_n))]).T
    trueM = np.concatenate((trueMl, trueMr), axis=0)

    # unknown target, coregulated
    untarget_n = M[-10:]
    # Covd, Covi = rand_cov(d=10, rho=.6)
    X2r = np.random.multivariate_normal(mu, covX, l)
    X2l = np.random.multivariate_normal(mu, np.diag(np.diag(covX)), 100-l)
    X2n = np.concatenate((X2l, X2r), axis=0)
    expression = (np.concatenate((Xn, trueM, falseM, X2n), axis=1))+3

    return genes, expression, target, Xn, M, trueM_n, trueM, falseM_n, falseM,\
        untarget_n, X2n


def make_groups_joint(n_samples=100, n_dim=50, rho_s=None):
    """Artificial dataset where feature subsets have different correlations."""
    # sequence number of dimensions
    feature_names = ["%s" % str(i) for i in np.arange(n_dim)]
    if rho_s is None:
        rho_s = [0.9, .8, .7, .6, .5, .4, .3, .2, .1, .05]

    # Create independent dimensions
    mu = np.zeros(n_dim)
    X_ind = np.random.multivariate_normal(mu, np.eye(n_dim), n_samples // 2)

    X_dep = None  # avoid linter error
    for i, rho in enumerate(rho_s):
        cov = random_covariance(n_dim // len(rho_s), rho)
        X_dep_0 = np.random.multivariate_normal(
            np.zeros(n_dim // len(rho_s)), cov, n_samples // 2)
        X_dep = np.hstack((X_dep, X_dep_0)) if i > 0 else X_dep_0

    X = np.vstack((X_dep, X_ind))
    y = np.ones(n_samples, dtype=int)
    y[n_samples // 2:] = -1

    # return also groups of correlated features
    groups = [np.arange(n_dim // len(rho_s)) + i * n_dim // len(rho_s)
              for i in range(len(rho_s))]
    return X, y, feature_names, groups
