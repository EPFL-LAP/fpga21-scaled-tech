"""Plots Graphs 11 through 13 of the paper.

Parameters
----------
data : str
    Name of the python source holding the data to be plotted.

Returns
-------
None
"""

import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--data")
args = parser.parse_args()

from importlib import import_module
data = import_module(args.data)

colors = plt.cm.get_cmap("Set1")

xs = range(0, len(data.curves[0][0]))

for i, curve in enumerate(data.curves):
    plt.plot(xs, [1e12 * t for t in curve[0]], label = curve[1], linewidth = 2, c=colors(float(i) / len(data.curves)), marker='o')

xticks = [float(len(xs)) / 8 * (i - 0.3333)  for i in range(1, 9)]
xticklabels = range(0, 8)

plt.ylim(10, 70)
plt.legend(loc="upper left")
plt.xlabel("Target LUT distance")
plt.xticks(xticks, xticklabels)
plt.ylabel("[ps]")
plt.title("K = 6, N = 8")
plt.tight_layout()
plt.savefig(args.data + ".pdf")
