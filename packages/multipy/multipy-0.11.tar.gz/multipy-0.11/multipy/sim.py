import matplotlib.pyplot as plt

import numpy as np

from scipy.stats import norm

import seaborn as sb

"""Compute the probability density functions."""
xloc, yloc = 0, 0.5
xscale, yscale = 1, 1

x = np.linspace(-3+xloc, 3+xloc, 100)
y = np.linspace(-3+yloc, 3+yloc, 100)

xpdf, ypdf = (norm.pdf(x, loc=xloc, scale=xscale),
              norm.pdf(y, loc=yloc, scale=yscale))

"""Visualize the PDFs."""
fig = plt.figure()

ax = fig.add_subplot(111)
ax.plot(x, xpdf)
ax.plot(y, ypdf)
ax.set_ylabel('Probability density')
ax.set_xlabel('Location parameter')

plt.show()
