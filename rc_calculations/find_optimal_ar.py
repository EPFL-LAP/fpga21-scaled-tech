"""Determines the RC optimal aspect ratio, given the pitch and relative permitivity.
Does so by performing a brute force search between 1.0 and 4.0, with increments of 0.05.

Parameters
----------
pitch : float
    Wire pitch [nm].
eps_rel : float 
    Relative permitivity.
inc_w : Optional[float], default = 0.0
    Fractional increase of copper width.
t_barrier : Optional[float], default = 3.0
    Barrier thickness. 
ar_max : Optional[float], default = 2.0
    Maximum aspect ratio. 

Returns
-------
float
    Optimal aspect ratio
float
    Copper width [nm]
float
    Copper height [nm]
float
    Line resistance [Ohm/um]
float
    Line capacitance [fF/um]
"""

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--pitch")
parser.add_argument("--eps_rel")
parser.add_argument("--inc_w")
parser.add_argument("--t_barrier")
parser.add_argument("--ar_max")

args = parser.parse_args()

pitch = float(args.pitch)
eps_rel = float(args.eps_rel)

inc_w = 0
try:
    inc_w = float(args.inc_w)
except:
    pass

t_barrier = 3.0
try:
    t_barrier = float(args.t_barrier)
except:
    pass

ar_min = 0.9
ar_inc = 0.1
ar_max = 2.0
try:
    ar_max = float(args.ar_max)
except:
    pass

ar = ar_min

best_hcu = -1
best_wcu = -1
best_ar = -1
best_R = -1
best_C = -1
best_RC = float('inf')
while ar <= ar_max:
    ar += ar_inc
    os.system("python calc_resistance.py --pitch %f --ar %f --inc_w %f --t_barrier %f > dump.txt" % (pitch, ar, inc_w, t_barrier))
    with open("dump.txt", "r") as inf:
        lines = inf.readlines()
    found = False
    for line in lines:
        if "Wcu" in line:
            best_wcu = float(line.split()[-1])
        elif "Hcu" in line:
            best_hcu = float(line.split()[-1])
        elif "Resistance" in line:
            found = True
            R = float(line.split()[2])
            break
    os.system("rm -rf dump.txt")
    if not found:
        continue
    os.system("python calc_capacitance.py --pitch %f --ar %f --eps_rel %f --inc_w % f > dump.txt" % (pitch, ar, eps_rel, inc_w))
    with open("dump.txt", "r") as inf:
        lines = inf.readlines()
    found = False
    for line in lines:
        if "Ct" in line:
            found = True
            C = float(line.split()[2])
            break
    os.system("rm -rf dump.txt")
    if not found:
        continue

    RC = R * C
    if RC < best_RC:
        best_RC = RC
        best_R = R
        best_C = C
        best_ar = ar

    print("AR", ar, "R", R, "C", C)
    print("RC = %.4f" % (R * C))

print("----------------------------------------------------------------\nBest results:\n")
print("AR = %.2f" % best_ar)
print("Wcu = %.1f nm" % best_wcu)
print("Hcu = %.1f nm" % best_hcu)
print("R = %.2f Ohm/um" % best_R)
print("C = %.2f fF/um" % best_C)
