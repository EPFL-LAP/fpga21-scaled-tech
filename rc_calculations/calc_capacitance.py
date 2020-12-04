"""Calculates the wire capacitance per unit length, using the ASU PTM formula
(ptm.asu.edu->Interconnect->Structure 2)

Parameters
----------
pitch : float
    Wire pitch [nm].
ar : float
    Aspect ratio of the wire (H / W).
layer : int
    Metal layer used.
eps_rel : float 
    Relative permitivity.
inc_w : Optional[float], default = 0.0
    Fractional increase of copper width.

Returns
-------
float
    Capacitance per unit length [fF/um]
"""
import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument("--pitch")
parser.add_argument("--ar")
parser.add_argument("--eps_rel")
parser.add_argument("--inc_w")

args = parser.parse_args()

pitch = float(args.pitch)
ar = float(args.ar)
eps_rel = float(args.eps_rel)

inc_w = 0
try:
    inc_w = float(args.inc_w)
except:
    pass

eps0 = 8.8541878128e-12
eps = eps0 * eps_rel


w = 0.5 * pitch * 1e-9
w *= 1 + inc_w
#Barrier is also metallic, hence it should not be deducted.

t = w * ar

h = w
#There is a via before the next layer, it has an AR close to 1, and contacts the wire itself,
#so we can assume it has the height of w. 

if h < 0:
    print("Metal height exceeds layer thickness.")
    raise ValueError

s = pitch * 1e-9 - w

Cg = eps * (w / h + 2.04 * ((s / (s + 0.54 * h)) ** 1.77) * ((t / (t + 4.53 * h)) ** 0.07))

Cc = eps * (1.41 * t / s * (math.e ** (-4 * s / (s + 8.01 * h))) + 2.37 * ((w / (w + 0.31 * s)) ** 0.28) * ((h / (h + 8.96 * s)) ** 0.76) * (math.e ** (-2 * s / (s + 6 * h))))

Ct = 2 * (Cg + Cc)

print("w = %.2e" % w)
print("t = %.2e" % t)
print("h = %.2e" % h)
print("s = %.2e" % s)


print("Cg = %.2e fF/um" % (Cg * 1e15 * 1e-6))
print("Cc = %.2e fF/um" % (Cc * 1e15 * 1e-6))
print("Ct = %.2e fF/um" % (Ct * 1e15 * 1e-6))
