# MIDAS

This repository contains python code that implements various estimators of entropy and mutual information.
In particular, Renyi Multi Information and Tsallis Multi Information estimators are available.

## Quickstart
Install `midas` from the Python Package Index by using `pip`, via
```bash
pip install midasML
```

Alternatively, you can clone it from our Github repository with

```bash
$ git clone https://github.com/SheffieldML/midas
```
and then install it with

```bash
$ python setup.py install
```
from the main folder of `midas`.

## Working example

To test `midas`, you can use the following example.
Create a toy dataset specifying the correlation between some variables.
```python
import numpy as np
from midas.estimator import RenyiMutualInformationDivergence, MIDAS
from midas.model_assessment import permutation_test_score_groups
from midas.utils import sample_generation

np.random.seed(30)
n_samples, n_dim = 30, 20
rho_s = [.95, .9, .8, 0, 0]
X, y, feature_names, groups = sample_generation.make_groups_joint(n_samples, n_dim, rho_s=rho_s)

estimator = RenyiMutualInformationDivergence(alpha=0.99, k=3, n_iter=20)
result = permutation_test_score_groups(MIDAS(estimator), X, y, groups, n_jobs=-1)
```
The first 3 groups of features are differentially co-regulated in half of the samples with respect to the other half, while the other groups of features are not (i.e., their co-regulation is the same in the two cases.)
Hence, we can use the `RenyiMutualInformationDivergence` to analyse the co-regulation for different classes of samples, by using `MIDAS` class.

`result` is a `pandas.DataFrame` which contains a summary of the result, which is something like

| | score        | perm_scores           | p-value  | group |
|-----| ------------- |:-------------:| -----:|:-----|
0 |	0.614204 |	[0.119599699041, 0.17002017399, 0.000642361597...|	0.009901|	[0, 1, 2, 3]
1	| 1.177062	|[0.00106705500132, 0.0115119749325, 0.00023392...|	0.009901	|[4, 5, 6, 7]
2	| 0.223355	|[0.0, 0.0410519694311, 0.00417966412452, 0.007...|	0.029703	|[8, 9, 10, 11]
3	| 0.010378	|[0.00187253953604, 0.00757194385644, 0.0002593...|	0.445545	|[12, 13, 14, 15]
4	| 0.000000	|[0.00307271647955, 0.0, 0.0129193052203, 0.010...|	1.000000	|[16, 17, 18, 19]

The first three results should have an high score and a low p-value, since the first three groups are differentially co-regulated by design (as specified before through the `rho_s` array). Hence, as in the example above, the method is capable to correctly address groups of variables as differentially co-regulated in the two classes of samples.

## Other examples
For other examples, please refer to Jupyter notebooks present in our Github page at
https://github.com/SheffieldML/midas/tree/master/notebooks.


