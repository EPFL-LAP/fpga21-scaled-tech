"""Simulates Fanout-of-4 delay for a given technology.

Parameters
----------
tech : int
    Node designator (16, 7, 5, 4, 3).
vdd : Optional[float], default = nominal
    Supply voltage.

Returns
-------
float
    Delay in picoseconds.
"""

import os
import math
import argparse
import sys
sys.path.insert(0,'..')

import setenv

import device_geometry

parser = argparse.ArgumentParser()
parser.add_argument("--tech")
parser.add_argument("--vdd")
args = parser.parse_args()

tech_node = int(args.tech)
node_index = device_geometry.node_names.index(tech_node)


GL = device_geometry.GL[node_index]
vdd = device_geometry.vdd[node_index]
try:
    vdd = float(args.vdd)
except:
    pass

spice_model_path = "\"%s/" % os.path.abspath("../spice_models/") + "%dnm.l\" %dNM_FINFET_HP\n"

##########################################################################
def gen_netlist():
    """Outputs the FO4 netlist.

    Parameters
    ----------
    None

    Returns
    -------
    str
        SPICE netlist.
    """

    txt = ".TITLE MAX_WL\n\n"
    txt += ".LIB %s\n" % (spice_model_path % (int(tech_node), int(tech_node)))
    txt += ".TRAN 1p 16n\n.OPTIONS BRIEF=1\n\n"

    txt += ".PARAM GL=%dn\n" % GL
    txt += ".PARAM supply_v=%.2f\n\n" % vdd

    
    txt += ".SUBCKT inv n_in n_out vdd D=1\n"
    txt += "MN1 n_out n_in gnd gnd nmos L=GL nfin=D\n"
    txt += "MP1 n_out n_in vdd vdd pmos L=GL nfin=D\n"
    txt += ".ENDS\n\n"

    txt += "Vps vdd gnd supply_v\n"
    txt += "Vin n_in gnd PULSE (0 supply_v 0 0 0 2n 4n)\n\n"

    txt += "Xinv1 n_in n_out_1 vdd inv D=1\n"
    txt += "Xinv4 n_out_1 n_out_4 vdd inv D=4\n"
    txt += "Xinv16 n_out_4 n_out_16 vdd inv D=16\n"
    txt += "Xinv64 n_out_16 n_out_64 vdd inv D=64\n\n"

    txt += ".MEASURE tfall TRIG V(n_out_1) VAL='supply_v/2' RISE=2\n"
    txt += "+                  TARG V(n_out_4) VAL supply_v/2 FALL=2\n\n"
    txt += ".MEASURE trise TRIG V(n_out_1) VAL='supply_v/2' FALL=2\n"
    txt += "+                  TARG V(n_out_4) VAL supply_v/2 RISE=2\n\n"

    txt += ".END"

    return txt
##########################################################################

##########################################################################
def measure():
    """Measures the FO4 delay.

    Parameters
    ----------
    None

    Returns
    -------
    float
        Delay.
    """
    with open("fo4.sp", "w") as outf:
        outf.write(gen_netlist())

    hspice_call = os.environ["HSPICE"] + " fo4.sp > hspice.dump"
    os.system(hspice_call)

    scale_dict = {'f' : 1e-15, 'p' : 1e-12, 'n' : 1e-9}

    with open("hspice.dump", "r") as inf:
        lines = inf.readlines()

    os.system("rm hspice.dump")

    for line in lines:
        if "tfall=" in line:
            tfall = float(line.split()[1][:-1]) * scale_dict[line.split()[1][-1]]
        elif "trise=" in line:
            trise = float(line.split()[1][:-1]) * scale_dict[line.split()[1][-1]]

    return (trise + tfall) / 2
##########################################################################

print("FO4 = %.2f ps" % (1e12 * measure()))
os.system("rm -rf fo4*")
