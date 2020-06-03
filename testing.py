from scipy.stats import f
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(1, 1)
dfn, dfd = 999, 999
mean, var, skew, kurt = f.stats(dfn, dfd, moments='mvsk')


x = np.linspace(f.ppf(0.01, dfn, dfd),
                 f.ppf(0.99, dfn, dfd), 100)
ax.plot(x, f.pdf(x, dfn, dfd),
        'r-', lw=5, alpha=0.6, label='f pdf')


rv = f(dfn, dfd)
ax.plot(x, rv.pdf(x), 'k-', lw=2, label='frozen pdf')

vals = f.ppf([0.001, 0.5, 0.999], dfn, dfd)
print(vals)
np.allclose([0.001, 0.5, 0.999], f.cdf(vals, dfn, dfd))

plt.show()