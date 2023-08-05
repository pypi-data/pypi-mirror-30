#!/usr/bin/env python
"""Utility function to retrieve previously estimated gamma parameters.

If the selected gamma is not present, calculate it and store it.

@author: Federico Tomasi
@email:  fdtomasi@gmail.com
"""
import numpy as np
import os

full_path = os.path.realpath(__file__)
thisdir = os.path.dirname(full_path)
gpath = thisdir+'/gamma/'


def get_gamma(d, k=3, alpha=.99):
    """Return a precomputed gamma value if present, or compute one.

    Parameters
    ----------
    d : int
        Data dimensionality.
    k : int
        -
    alpha : float, optional
        Parameter for estimating gamma empirically.

    Returns
    -------
    gamma : float
    """
    gamma = 0

    if d == 3:
        filename = 'gamma_3d_20M.txt'
    elif d in (10, 20):
        filename = 'gamma_%dd_10M.txt' % d
    elif 3 < d < 20:
        filename = 'gamma_%dd_500K.txt' % d
    elif 20 < d < 101 or d in range(103, 183, 5) or d == 182:
        filename = 'gamma_%dd_100K.txt' % d
    elif d in [183]:
        filename = 'gamma_%dd_50K.txt' % d
    else:
        # not have the required gamma
        print('Empirically compute gamma ...')
        import parameters_estimation as est
        gamma = est.compute_gamma_emp(d, k, alpha, 50000)
        np.savetxt('gamma_%dd_50K.txt' % d, [gamma])
        return gamma
    gamma = float(np.loadtxt(gpath+filename))
    print('gamma loaded: %.16f' % gamma)
    return gamma
