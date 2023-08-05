#!/usr/bin/env python
"""Analytical formulas for Renyi-, Tsallis-, KL-divergences.

Formulas are calculated according to Szabo's formulas.

@author: Federico Tomasi
@email:  fdtomasi@gmail.com
"""
import sys
import numpy as np
from numpy import log, diag, prod
from numpy.linalg import det, inv

from sklearn.utils.extmath import fast_logdet


def renyi_information_analytical(C, alpha=.99, distr='normal'):
    """Renyi Mutual Information analytical value for a Gaussian (normal)
    distribution, from the covariance matrix.

    Following the example of Szabo, the Renyi mutual information can be
    analytically computed using the covariance matrix.
    (Add Szabo link)

    Parameters
    ----------
    C : array_like
        Covariance matrix
    alpha : float, optional
        -
    distr : string, optional
        Identify the data distribution. For now, only normal distribution
        is supported.
    """
    if distr == 'normal':
        tmp1 = - alpha / 2. * fast_logdet(C)
        tmp2 = - (1. - alpha) / 2. * log(prod(diag(C)))
        tmp3 = log(det(alpha*inv(C) + (1.-alpha)*diag(1./diag(C)))) / 2.
        return 1. / (alpha-1.) * (tmp1+tmp2-tmp3)
    else:
        sys.stderr.write('Distribution {} unknown.\n'.format(distr))
    return -1


def renyi_information_distributions_analytical(Cf, Cg, alpha=.99, distr='normal'):
    """Renyi Mutual Information analytical value between two different
    distributions, from their covariance matrices.

    Following the example of Szabo, the Renyi mutual information can be
    analytically computed using the covariance matrix.
    (Add Szabo link)

    Parameters
    ----------
    Cf, Cg : array_like
        Covariance matrices of two distributions.
    alpha : float, optional
        -
    distr : string, optional
        Identify the data distribution. For now, only normal distribution
        is supported.
    """
    if distr == 'normal':
        tmp1 = -alpha / 2. * log(det(Cf))
        tmp2 = -(1.-alpha) / 2. * log(det(Cg))
        tmp3 = log(det(alpha*inv(Cf) + (1.-alpha)*inv(Cg))) / 2.
        return 1. / (alpha-1.) * (tmp1+tmp2-tmp3)
    else:
        sys.stderr.write('Distribution {} unknown.\n'.format(distr))
    return -1


# derived, ?
def tsallis_i(Cf, Cg, alpha=.99, distr='normal'):
    """Tsallis Mutual Infomation analytical value between two different
    distributions, from their covariance matrices.

    Parameters
    ----------
    Cf, Cg : array_like
        Covariance matrices of the two distributions.
    alpha : float, optional
        -
    distr : string, optional
        Identify the data distribution. For now, only normal distribution
        is supported.
    """
    if distr == 'normal':
        tmp1 = det(Cf)**(-alpha/2.)
        tmp2 = det(Cg)**(-(1.-alpha)/2.)
        tmp3 = det(alpha*inv(Cf) + (1.-alpha)*inv(Cg))**.5
        return 1. / (alpha-1.) * (tmp1*tmp2/tmp3 - 1.)
    else:
        sys.stderr.write('Distribution {} unknown.\n'.format(distr))
    return -1


def _renyi_i_beta(par_d, par_i, d):
    """DEPRECATED.

    Derives from lemma 14.
    """
    from scipy.special import beta
    tmp1, tmp2, tmp3 = 1, 1, 1
    for i in range(d):
        a, b, c, d = par_d[0], par_d[1], par_i[0], par_i[1]
        tmp1 *= (beta(2*a - 1, 2*b - 1) / beta(a, b)**2)
        tmp2 *= (beta(2*c - 1, 2*d - 1) / beta(c, d)**2)
        tmp3 *= (beta(a + c - 1, b + d - 1) / (beta(a, b) * beta(c, d)))

    return (tmp1 + tmp2 - 2*tmp3)**.5


def _renyi_i_beta2(par_d, par_i, d, alpha):
    """DEPRECATED.

    Derives from lemma 12.
    """
    from scipy.special import gamma
    tmp = 1
    for i in range(d):
        a, b, c, d = par_d[0, i], par_d[1, i], par_i[0, i], par_i[1, i]

        tmp1 = (gamma(a+b))**alpha / ((gamma(a))**alpha*(gamma(b)**alpha))
        tmp2 = (gamma(c+d))**(1-alpha) / ((gamma(c))**(1-alpha)*(gamma(d)**(1-alpha)))
        tmp3 = (gamma(alpha*(a-1)+(1-alpha)*(c-1))*gamma(alpha*(b-1)+(1-alpha)*(d-1))) / (gamma(alpha*(a-1)+(1-alpha)*(c-1)+alpha*(b-1)+(1-alpha)*(d-1)))
        tmp *= (tmp1 * tmp2 * tmp3)
    return np.log(tmp) / (alpha-1), tmp


def kl_divergence(Cf, Cg):
    """Kullback Leibler divergence between two distributions.

    Parameters
    ----------
    Cf, Cg : array_like
        Covariance matrices of the two distributions.
    """
    tmp1 = np.trace(inv(Cg) * Cf)
    tmp2 = fast_logdet(Cg) - fast_logdet(Cf)
    tmp = tmp2 + tmp1 - Cf.shape[1]
    return .5 * tmp
