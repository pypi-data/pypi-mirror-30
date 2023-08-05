"""Model assessment module for entropy."""
import pandas
import scipy

from sklearn.model_selection._validation import permutation_test_score


def benjamini_hochberg_correction(pvalues):
    """Correct pvalues with BH correction."""
    pval_len = len(pvalues)
    ranks = scipy.stats.rankdata(pvalues, method='ordinal')
    # pvals = np.asarray(pvalues)
    # pvals *= ranks
    # pvals /= pval_len
    # return pvals
    return [1. * pval * rank / pval_len for pval, rank in zip(pvalues, ranks)]


def permutation_test_score_groups(
        estimator, X, y, groups, cv=None, n_permutations=100, n_jobs=1,
        random_state=0, verbose=0, scoring=None, constrain_groups=None,
        benjamini_hochberg=False):
    """Evaluate the significance of a cross-validated score with permutations.

    Read more in the :ref:`User Guide <cross_validation>`.

    Parameters
    ----------
    estimator : estimator object implementing 'fit'
        The object to use to fit the data.

    X : array-like of shape at least 2D
        The data to fit.

    y : array-like
        The target variable to try to predict in the case of
        supervised learning.

    groups : list of array-like
        List of groups of variables, for which to compute the mutual
        information.

    constrain_groups : array-like, with shape (n_samples,), optional
        Labels to constrain permutation within groups, i.e. ``y`` values
        are permuted among samples with the same group identifier.
        When not specified, ``y`` values are permuted among all samples.

        When a grouped cross-validator is used, the group labels are
        also passed on to the ``split`` method of the cross-validator. The
        cross-validator uses them for grouping the samples  while splitting
        the dataset into train/test set.

    scoring : string, callable or None, optional, default: None
        A string (see model evaluation documentation) or
        a scorer callable object / function with signature
        ``scorer(estimator, X, y)``.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
          - None, to use the default 3-fold cross validation,
          - integer, to specify the number of folds in a `(Stratified)KFold`,
          - An object to be used as a cross-validation generator.
          - An iterable yielding train, test splits.

        For integer/None inputs, if the estimator is a classifier and ``y`` is
        either binary or multiclass, :class:`StratifiedKFold` is used. In all
        other cases, :class:`KFold` is used.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validation strategies that can be used here.

    n_permutations : integer, optional
        Number of times to permute ``y``.

    n_jobs : integer, optional
        The number of CPUs to use to do the computation. -1 means
        'all CPUs'.

    random_state : RandomState or an int seed (0 by default)
        A random number generator instance to define the state of the
        random permutations generator.

    verbose : integer, optional
        The verbosity level.

    benjamini_hochberg : bool, optional, default False
        If True, convert p-values with the Benjamini-Hochberg correction
        for multiple sampling.

    Returns
    -------
    dataframe : pandas.DataFrame
        Each row contains the the result on a group, plus the information on
        the group. See `permutation_test_score` for the other values
        on the row.

    """
    # result = [permutation_test_score(
    #     estimator, X, y, group, n_permutations=n_permutations, n_jobs=n_jobs,
    #     random_state=random_state, verbose=verbose, scoring=scoring,
    #     groups=constrain_groups, cv=cv) for group in groups]
    result = [permutation_test_score(
        estimator, X[:, group], y, n_permutations=n_permutations,
        n_jobs=n_jobs, random_state=random_state, verbose=verbose,
        scoring=scoring, groups=constrain_groups, cv=cv) for group in groups]

    dataframe = pandas.DataFrame(result).rename(columns={
        0: 'score', 1: 'perm_scores', 2: 'p-value'})
    dataframe['group'] = groups

    if benjamini_hochberg:
        dataframe['p-value'] = benjamini_hochberg_correction(
            dataframe['p-value'])

    return dataframe
