**RLCluster**
=============

This is the repository for the *rlcluster* Python package that implements the Rodriguez-Laio 
clustering method [(*Science*, 2014,  **344**, 1492-1495)](http://science.sciencemag.org/content/344/6191/1492)

-------

## Installation

`pip install rlcluster`

---

## Usage

```python
import rlcluster as rlc
# The only required input is a square-form distance matrix:
result = rlc.cluster(D)
# Useful things are attributes of the result object:
a = result.assignments # point i belongs to cluster a[i]
r = result.rhos # point i has RL local density value r[i]
d = result.deltas # point i has RL delta value d[i]
c = result.centres # The list of points that qualify as cluster centres
cutoff = result.cutoff # The cutoff delta value in the decision graph used to select cluster centres
# If you have matplotlib, you can view the decision graph:
import matplotlib pyplot as plt
rlc.decision_graph(result, plt.axes())
```
By default cluster() uses a cutoff distance for the local density calculation that will put an average of 
2% of all the points into each cluster, but this can be changed:
```python
result = rlc.cluster(D, target_fraction=0.01) # aim for clusters of average size 1% of the total
```
By default the cutoff delta value for identifying cluster centres from the decision graph (rho vs. delta) is set at
5 sigma above the mean, but this can also be changed:
```python
result = rlc.cluster(D, sigma=7.0) 
```
Finally the default method for calculating local densities uses a Gaussian kernel rather than the simple hard distance
cutoff method described in the original paper (though the kernel method is used in parts of it). The orignal approach 
can be enforced:
```python
result = rlc.cluster(D, method='classic')
```

------
#Author

Charlie Laughton 2018

#License

BSD (2-clause)


