"""Render docs/example.png for the README."""
import numpy as np

import llplot

llplot.setup()
n = np.logspace(1, 5, 40)
fig, (left, right) = llplot.figure("double", ncols=2)
llplot.lines(left, n, {"Monte Carlo": n**-0.5, "Sobol QMC": 2 * np.log(n) / n}, err={"Monte Carlo": 0.3 * n**-0.5})
left.set(xscale="log", yscale="log", xlabel="samples $N$", ylabel="RMS error")
x = np.linspace(-1, 1, 101)
llplot.image(right, np.outer(np.sin(3 * x), x), label="residual (a.u.)", diverging=True)
right.set(xticks=[], yticks=[])
llplot.savefig(fig, "docs/example.png", max_kb=150)
