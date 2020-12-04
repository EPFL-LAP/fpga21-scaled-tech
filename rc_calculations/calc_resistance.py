"""Calculates the wire resistivity based on the model of Ciofi et al.
>>Impact of Wire Geometry on Interconnect RC and Circuit Delay<< (equation (1)),
by integrating the formula assuming no tapering. In this case the calculation
reduces to a table integral.

Parameters
----------
w : float
    Copper width in nm.
h : float
    Copper height in nm.
pitch : float
    Wire pitch [nm].
ar : float
    Aspect ratio of the wire (H / W).
inc_w : Optional[float], default = 0.0
    Fractional increase of copper width.
t_barrier : Optional[float], default = 3.0
    Barrier thickness. 

Notes
-----
Either (w_cu, h_cu), (pitch, ar), (w_cu, ar), or (h_cu, ar) can be specified).

Returns
-------
float
    Resistance per unit length [Ohm/um]
"""

import argparse
from math import sinh, cosh

parser = argparse.ArgumentParser()
parser.add_argument("--w")
parser.add_argument("--h")
parser.add_argument("--pitch")
parser.add_argument("--ar")
parser.add_argument("--inc_w")
parser.add_argument("--t_barrier")
args = parser.parse_args()

barrier = 3.0
try:
    barrier = float(args.t_barrier)
except:
    pass

w_cu = -1
try:
    w_cu = float(args.w)
except:
    pass
h_cu = -1
try:
    h_cu = float(args.h)
except:
    pass
pitch = -1
try:
    pitch = float(args.pitch)
except:
    pass
ar = -1
try:
    ar = float(args.ar)
except:
    pass

inc_w = 0
try:
    inc_w = float(args.inc_w)
except:
    pass

if w_cu < 0:
    if h_cu > 0 and ar > 0:
        w_cu = h_cu / ar
    elif pitch > 0:
        w_cu = pitch / 2
    else:
        print("Please specify either copper width, height and the aspect ratio, or the wire pitch.")
        exit(-1)

w_cu *= 1 + inc_w

if h_cu < 0:
    if ar > 0:
        h_cu = w_cu * ar
    else:
        print("Please specify the copper height or the aspect ratio.")
        exit(-1)

rho_b = 32.05
rho_q = 82
lambda_q = 3.75
"""Parameters taken from Ciofi2016"""

w_cu -= 2 * barrier
h_cu -= barrier

rho_tot = rho_b * w_cu * h_cu + rho_q * (h_cu / (cosh(w_cu / (2 * lambda_q))) * lambda_q * 2 * sinh(0.5 * w_cu / lambda_q)\
                                        + w_cu / (cosh(h_cu / (2 * lambda_q))) * lambda_q * 2 * sinh(0.5 * h_cu / lambda_q))

rho_avg = rho_tot / (h_cu * w_cu)

R = rho_avg / (h_cu * w_cu)

print("Wcu = %.1f" % w_cu)
print("Hcu = %.1f" % h_cu)
print("Resistance = %f Ohm/um" % (R * 1e3))
