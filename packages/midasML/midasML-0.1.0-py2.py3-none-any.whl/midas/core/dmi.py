# -*- coding: utf-8 -*-
"""
Core function for DMI method.

@author: Federico Tomasi
@email:  fdtomasi@gmail.com
"""
import os
import time
import numpy as np

from ..estimators.mi_estimators import estimate_mi
from ..utils import utilities as utl


def dmi_method(tumors, notumors, map_platform, map_target, gsname, ann=None,
               fc_limit=-1, L=1000, **mikwargs):
    """Execute DMI method on the dataset.

    Parameters
    ----------
    tumours, notumours : array_like
        DxN matrix of N i.i.d samples for D random variables.
    map_platform : list
        List of genes in the dataset.
    map_target : list
        List of genes in the gene set to analyse.
    gsname : string
        Name of the gene set.
    ann : array_like, optional
        Annotation file, mapping between EntrezID and official symbols.
    fc_limit : float, optional
        If higher than 0, discard genes with small FC.
    L : int, optional
        Number of random sampling for the computation of the p-value.
    mikwargs : dict, optional
        Parameters for the computation of Renyi Mutual Information.

    Returns
    -------
    pvalue : float
        The percentage of times in which random gene sets has higher DMI
        values with respect to the original gene set.

    """
    # must have the same number of genes
    assert(tumors.shape[0] == notumors.shape[0])
    idx = []  # to manage the possibility of value non-existence
    gID = []
    for x in map_target:
        try:
            idx.append(map_platform.index(x))
            gID.append(x)
        except ValueError:
            pass
    if len(idx) < 2:  # cannot compute mutual information
        return 0, 0, 0, 1.  # TODO fix? better error handling
    T, NT = tumors[idx, :], notumors[idx, :]

    gID = np.array(gID)
    d = T.shape[0]
    fc = np.zeros((d, 3))
    for i in range(d):
        fc[i, 0] = np.mean(T[i, :])
        fc[i, 1] = np.mean(NT[i, :])
        fc[i, 2] = abs(np.log(fc[i, 0]) - np.log(fc[i, 1]))

        if fc_limit > 0 and fc[i, 2] < fc_limit:
            np.delete(T, i, 0)
            np.delete(NT, i, 0)
            d = d - 1

    # RMI in controland positive samples
    rmi_ctrl = estimate_mi(NT, **mikwargs)
    rmi_dsse = estimate_mi(T, **mikwargs)
    dmi = rmi_dsse - rmi_ctrl

    pval = utl.pvalue(tumors, notumors, abs(dmi), d, L, **mikwargs)
    pval_str = '%.3e' % pval

    # Print information within gene set
    # TODO porting to pandas.DataFrame
    resGS = np.empty([d, 5+T.shape[1]+NT.shape[1]], dtype=object)
    col = ['EID', 'SYM', 'AVG_T', 'AVG_NT', 'log2FC']
    for i in range(T.shape[1]):
        col.append('EXP_%dT' % i)
    for i in range(NT.shape[1]):
        col.append('EXP_%dNT' % i)
    cols = np.array(col)[np.newaxis, :]

    for i in range(d):
        resGS[i, 0] = gID[i]
        if ann is not None:
            try:
                resGS[i, 1] = ann[list(ann[:, 0]).index(gID[i]), 1]
            except ValueError:
                resGS[i, 1] = '-'
        else:
            resGS[i, 1] = '-'
        resGS[i, 2] = fc[i, 0]  # mean expression controls
        resGS[i, 3] = fc[i, 1]  # mean expression disease
        resGS[i, 4] = fc[i, 2]  # FC
        resGS[i, 5:T.shape[1]+5] = T[i, :]
        resGS[i, T.shape[1]+5:] = NT[i, :]
    resGS = np.concatenate((cols, resGS[np.argsort(resGS[:, 4])][::-1]))

    if not os.path.exists('resgs'):
        os.makedirs('resgs')
    np.savetxt('resgs/res_%s' % gsname, resGS, delimiter=',', fmt='%s')

    return dmi, rmi_dsse, rmi_ctrl, pval_str


def run_dmi(tumors, notumors, map_platform, genesets, outfile='res_DMI',
            ann=None, fc_limit=-1, alpha=.99, k=3,
            gamma=0, L=1000, niter=10, etype=1, use_copula=False,
            normalise=False, nonnegative=True, pval_threshold=0.05):
    """Execute DMI method on the dataset.

    Parameters
    ----------
    tumours : array_like
        DxN matrix of N i.i.d samples for D random variables.
    notumours : array_like
        DxM matrix of M i.i.d samples for D random variables.
    map_platform : list
        List of genes in the dataset.
    genesets : string
        Filename of the gene set list.
    outfile : string, optional
        Output filename.
    ann : array_like, optional
        Annotation file, mapping between EntrezID and official symbols.
    fc_limit : float, optional
        If higher than 0, discard genes with small FC.
    alpha : float, optional
        Coefficient for the Renyi mutual information.
    k : int, optional
        Number of neighbours to consider in the computation of Renyi MI.
    gamma : float, optional
        Constant. Estimated from the function 'compute_gamma'.
        Default: 0 (unused)
    L : int, optional
        Number of random sampling for the computation of the p-value.
    niter : int, optional
        Number of single iterations for each random sampling.
    etype : int, optional
        Type of mutual information estimator.
        Values:
            0: 'mi_estimator_gamma'
            1: 'renyi_i_d' (default)
            2: 'renyi_i_weighted'
    use_copula : bool, optional
        Transform input points through empirical copula.
    normalise : bool, optional
        Normalise the mutual information value by sqrt(d), so that the
        mutual information between variables with different dimensions is more
        comparable.
    nonnegative : bool, optional
        Cut negative values to zero.
    pval_threshold : float, optional
        if higher than 0, discard gene sets with higher p-value.
        Default: 0.05

    Returns
    -------
    None.

    """
    # t = time.time()
    ngs = utl.file_len(genesets)  # number of gene sets
    cols = np.array(['NGS', 'Tumor RMI', 'Non tumor RMI', 'DMI',
                     'p-value', '+-', 'BH corrected p-value'])[np.newaxis, :]
    res = np.empty([ngs, cols.shape[1]], dtype=object)

    with open(genesets, 'r') as f:
        i = 0
        for line in f:
            name, descr, targets = line.split('\t', 2)
            map_target = targets.split('\t')
            res[i, 0] = name
            utl.progressbar(i+1, ngs, name)
            res[i, 3], res[i, 1], res[i, 2], res[i, 4] = \
                dmi_method(tumors, notumors, map_platform, map_target, name,
                           ann=ann, fc_limit=fc_limit, L=L,
                           alpha=alpha, k=k, gamma=gamma, niter=niter,
                           etype=etype,
                           use_copula=use_copula, normalise=normalise,
                           nonnegative=nonnegative)
            if res[i, 3] < 0:
                res[i, 3] = abs(res[i, 3])
                res[i, 5] = '-'
            else:
                res[i, 5] = '+'
            i = i + 1

    res = res[np.argsort(res[:, 3])][::-1]

    bh_pval_floats = np.array(utl.bh_pval_correction(np.array(res[:, 4], dtype=float)))
    res[:, -1] = bh_pval_floats

    if pval_threshold > 0:
        # remove gene set with high pvals
        res = res[np.array(res[:, -1]) < pval_threshold]
    res[:, -1] = np.array(['%.3e' % x for x in res[:, -1]])

    res = np.concatenate((cols, res))
    np.savetxt(outfile + '_' + utl.get_time() + '.csv', res,
               delimiter=',', fmt='%s')
    print
    print res
