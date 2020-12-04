"""Scales delays between technologies, based on the scaling model from:
Stillmaker and Baas >>Scaling Equations for the Accurate Prediction of
CMOS Device Performance from 180nm to 7nm<<. All nominal voltages were
taken from the appropriate PTM NMOS model.

Parameters
----------
tf : int
    The source technology node designator.
tt : int
    The target technology node designator.
delay : float
    The delay to be scaled, in seconds.

Returns
-------
float
    The delay in the target technology.
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--tf")
parser.add_argument("--tt")
parser.add_argument("delay")

args = parser.parse_args()

tf = int(args.tf)
tt = int(args.tt)
td = float(args.delay)

coeffs = {\
          45 : [-501.6, 1567, -1619, 566.1],\
          14 : [-40.66, 109.2, -100.6, 35.92],\
          10 : [-34.95, 93.65, -85.99, 30.4],\
           7 : [-28.58, 76.6, -70.26, 24.69],\
         }

nominal_vdd = {45 : 1.0, 14 : 0.8, 10 : 0.75, 7 : 0.7}

delay_factor = lambda t : sum([coeffs[t][3 - e] * nominal_vdd[t] ** e for e in range(3, -1, -1)])

##########################################################################
def to_units(td):
    """Pretty prints the time in the right units.

    Parameters
    ----------
    td : float
        The time to be printed.
    
    Returns
    -------
    str
        The printed time
    """

    if td > 1e-6:
        return "%.4f us" % (td * 1e6)
    if td > 1e-9:
        return "%.4f ns" % (td * 1e9)
    if td > 1e-12:
        return "%.4f ps" % (td * 1e12)
    
    return "%.4f fs" % (td * 1e15)
##########################################################################

from_7nm = {5 : 4.69 / 4.96, 4 : 4.69 / 4.96, 3 : 4.48 / 4.96}
#Previously measured through sim_fo4.py    

if not tf in coeffs:
    print("Source technology not available. Please choose from: " + str(sorted(coeffs.keys(), reverse = True)))
    raise ValueError

if not tt in coeffs:
    if tt in from_7nm:
        new_delay = (td * delay_factor(7)) / delay_factor(tf)
        new_delay *= from_7nm[tt]
        print(new_delay)
        print(to_units(new_delay))
        exit(0)
    else:
        print("Target technology not available. Please choose from: "\
              + str(sorted(list(coeffs.keys()) + list(from_7nm.keys()), reverse = True)))
        raise ValueError

new_delay = (td * delay_factor(tt)) / delay_factor(tf)

print(new_delay)
print(to_units(new_delay))
