"""Calculates via resistance using the model in >>calc_resistance.py<<
and parameters from Ciofi et al., >> Modeling of via resistance for advancedtechnology nodes<<.

Parameters
----------
pitch1 : float
    Wire pitch [nm] on the bottom layer.
inc_w1 : Optional[float], default = 0.0
    Fractional increase of copper width on the bottom layer.
pitch2 : float
    Wire pitch [nm] on the top layer.
inc_w2 : Optional[float], default = 0.0
    Fractional increase of copper width on the top layer.
ar : float
    Aspect ratio of the via (H / W).
t_barrier_bottom : Optional[float], default = 3.0
    Bottom barrier thickness. 
t_barrier_top : Optional[float], default = 4.0
    Top barrier thickness.
via_height : Optional[float], default = derived from ar
    Override the via height.

Returns
-------
float
    Heignt [nm]
float
    Resistance [Ohm]
"""

import math
import os

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--pitch1")
parser.add_argument("--inc_w1")
parser.add_argument("--pitch2")
parser.add_argument("--inc_w2")
parser.add_argument("--ar")
parser.add_argument("--t_barrier_bottom")
parser.add_argument("--t_barrier_top")
parser.add_argument("--via_height")

args = parser.parse_args()

pitch1 = float(args.pitch1)
inc_w1 = 0
try:
    inc_w1 = float(args.inc_w1)
except:
    pass

pitch2 = float(args.pitch2)
inc_w2 = 0
try:
    inc_w2 = float(args.inc_w2)
except:
    pass

ar = 1.0
try:
    ar = float(args.ar)
except:
    pass


top_barrier = 4.0

bottom_barrier = 3.0

try:
    top_barrier = float(args.t_barrier_top)
except:
    pass

try:
    bottom_barrier = float(args.t_barrier_bottom)
except:
    pass

barrier_res = 1200.0

w1 = pitch1 * 0.5 * (1 + inc_w1)
via_height = w1 * ar
try:
    via_height = float(args.via_height)
except:
    pass

w1 -= 2 * bottom_barrier
w2 = pitch2 * 0.5 * (1 + inc_w2) - 2 * top_barrier

w_cu = w2

alpha = math.radians(3)

h_min = w1
h_max = w1 + via_height * math.tan(alpha)

h_cu = 0.5 * (h_min + h_max)

#We already subtracted the barrier, hence t_barrier = 0.0
os.system("python calc_resistance.py --t_barrier 0.0 --w %f --h %f > dump.txt" % (w_cu, h_cu))
with open("dump.txt", "r") as inf:
    lines = inf.readlines()
    for line in lines:
        if "Resistance" in line:
            found = True
            R = float(line.split()[2])
            break
    os.system("rm -rf dump.txt")

top_barrier_contact_area = w2 * h_max
bottom_barrier_contact_area = w2 * h_min

R_barrier = barrier_res * (top_barrier / top_barrier_contact_area + bottom_barrier / bottom_barrier_contact_area)

R_via = R * 1e-3 * (via_height - bottom_barrier) + R_barrier

print("H = %.1f nm" % via_height)
print("R = %.2f Ohm" % R_via)
