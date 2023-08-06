import numpy as np
from scipy.stats import invgamma, gamma

from dglm import NormalDLM
from filters import KalmanFilter
from structure import UnivariateStructure


class Gibbs:
    def __init__(self, structure, m0, C0, vprior, wprior, data):
        self._structure = structure
        self._m0 = m0
        self._C0 = C0
        self._vprior = vprior
        self._wprior = wprior
        self._data = data
        self._nobs = len(data)

    def _states(self, V, W):
        ms = [self._m0]
        Cs = [self._C0]
        structure = self._structure
        structure._W = W
        kf = KalmanFilter(structure=self._structure, V=V)
        for t in range(1, self._nobs):
            # TODO: Obs don't start in 1! but in 0!
            m, C = kf.filter(self._data[t], ms[t-1], Cs[t-1])
            ms.append(m)
            Cs.append(C)
        return ms, Cs

    def run(self, V, W):
        Ft = self._structure.F.T
        _V = V
        _W = W
        n = self._nobs
        for i in range(1000):
            ms, Cs = self._states(V=_V, W=_W)

            ssy = np.zeros(n)
            sstheta = np.zeros((n, len(self._wprior)))
            for t in range(1, n):
                ssy[t-1] = np.power(self._data[t] - Ft * ms[t], 2.0)
                sstheta[t-1] = np.power(ms[t] - self._structure.G * ms[t-1], 2.0)

            # TODO: rows is t! columns is component!
            print("====="*10)

            v_rate = self._vprior + (0.5 * sum(ssy))
            _V = 1.0 / gamma(self._vprior + 0.5 * n, scale=1.0/v_rate).rvs()

            w_rate = [self._vprior + (0.5 * d) for d in sstheta.sum(axis=0)]
            _W = np.diag([1.0 / gamma(self._vprior + (0.5 * n), scale=1.0/d).rvs() for d in w_rate])
            print("V = {}".format(_V))
            print("W = {}".format(_W))



if __name__=='__main__':
    import csv
    # # import matplotlib.pyplot as plt
    # nile = {'time': [], 'value': []}
    # with open('docs/data/Nile.csv') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         nile['time'].append(int(row['time']))
    #         nile['value'].append(int(row['value']))
    # # plt.plot(nile['time'], nile['value'])
    # # plt.axvline(x=1898, ls='--', c='black', alpha=0.3)
    # # plt.show()

    lc = UnivariateStructure.locally_constant(W=2.2)
    m0 = np.array([0])
    C0 = np.identity(1)*100
    ndlm = NormalDLM(structure=lc, V=1.5)
    obs = [None]
    states = [m0]
    for i in range(1, 1000):
        states.append(ndlm.state(states[i-1]))
        obs.append(ndlm.observation(states[i]))


    # gibbs = Gibbs(lc, m0, C0, 1, [1], nile['value'])
    gibbs = Gibbs(lc, m0, C0, 1, [1], obs)
    gibbs.run(V=1, W=1)
    # print(ms)
    # print(Cs)