import numpy as np
import networkx as nx


def _rho(D, target_fraction=0.02, mode='gaussian'):
    """Calculates the RL rho values from a distance matrix"""
    dcut = np.sort(D)[:,1 + int(len(D) * target_fraction)].mean()
    if mode == 'classic':
        r = np.array([len(np.where(d < dcut)[0]) for d in D])
    elif mode == 'gaussian':
        r = np.exp(-D ** 2/(dcut**2)).sum(axis=0)
    else:
        raise ValueError('Error: unknown density mode {}'.format(mode))
    return r

def _delta(D, rho):
    """Calculated the RL delta values for points in a distribution"""
    m = D.max() + 1.0
    dm = D + np.identity(len(D)) * m
    idel = [np.where(rho <= rho[i], m, dm[i]).argmin() for i in range(len(rho))]
    d = [D[i, idel[i]] for i in range(len(idel))]
    idel[rho.argmax()] = rho.argmax()
    d[rho.argmax()] = max(d) + 1.0
    return np.array(d), np.array(idel)

def _centres(d, sigma=10.0):
    """Find the centres in an RL clustering"""
    dmean = d.mean()
    dstdev = d.std()
    dthresh = dmean + dstdev * sigma
    centres = []
    for i in range(len(d)):
        if d[i] > dthresh:
            centres.append(i)
    return np.array(centres), dthresh

class RLClusterResult(object):
    """The result from an RL clustering"""
    def __init__(self):
        assignments = None
        rhos = None
        deltas = None
        centres = None
        threshold = None

def cluster(d, target_fraction=0.02, sigma=5.0, mode='gaussian'):
    """Do Rodriguez-Laio clustering on a square-form distance matrix"""
    D = np.array(d)
    if len(D.shape) != 2:
        raise ValueError('Error - the input is not a 2D matrix')
    if D.shape[0] != D.shape[1]:
        raise ValueError('Error - the input distance matrix is not square')
    if target_fraction < 0 or target_fraction > 1.0:
        raise ValueError('Error: target fraction must be between 0.0 and 1.0')
    if not mode in ['gaussian', 'classic']:
        raise ValueError('Error: unknown density mode {}'.format(mode))
    r = _rho(D, target_fraction=target_fraction, mode=mode)
    d, id = _delta(D, r)
    o, dthresh = _centres(d, sigma=sigma)
    dg = nx.DiGraph()
    for i in range(len(id)):
        if not i in o:
            dg.add_edge(i, id[i])
    wcc = nx.weakly_connected_components(dg)
    cids = np.zeros(len(d))
    id = 0
    for wc in wcc:
        id += 1
        cids[list(wc)] = id
    result = RLClusterResult()
    result.assignments = np.array(cids)
    result.centres = np.array(o)
    result.rhos = np.array(r)
    result.deltas = np.array(d)
    result.threshold = dthresh
    return result

def decision_graph(result, axes):
    """Plot an RL decision graph on a set of matplotlib axes"""
    try:
        from matplotlib import pyplot as plt
    except ImportError:
        raise RuntimeError('Error: RLdecisionGraph() requires matplotlib')
    for id in np.unique(result.assignments):
        axes.plot(result.rhos[result.assignments==id], result.deltas[result.assignments==id], 'o')
    axes.plot([result.rhos.min(), result.rhos.max()], [result.threshold, result.threshold], '--')

