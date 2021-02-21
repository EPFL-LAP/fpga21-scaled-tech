""""Determines the minimum grid size for each circuit and cluster size combination.

Parameters
----------
None

Returns
-------
Dict[int, Dict[str, int]]
    Dictionary of square grid sizes.
"""

import os
import sys
sys.path.insert(0,'../../')

import setenv

circ_dir = os.path.abspath("../runner_scripts/benchmarks/")
Ns = [2, 4, 8, 16]
arc_filename = "k6_N%d_40nm.xml"

vpr_flags = ["--pack",\
             " > /dev/null"]

os.mkdir("run/")

size_dict = {}
for N in Ns:
    print("N = %d" % N)
    size_dict.update({N : {}})
    for f in sorted(os.listdir(circ_dir)):
        print(f)
        circ = circ_dir + '/' + f
        arc = os.path.abspath(arc_filename % N)
        os.system("cp %s run/circ.blif" % circ)
        os.system("cp %s run/arc.xml" % arc)
        os.chdir("run/")
        vpr_args = ["arc.xml", "circ.blif"]
        os.system(' '.join([os.environ["VPR"]] + vpr_args + vpr_flags))
        with open("vpr_stdout.log", "r") as inf:
            lines = inf.readlines()
        for line in lines:
            if "FPGA sized to" in line:
                size_dict[N].update({os.path.basename(circ).rsplit(".blif", 1)[0] : int(line.split()[3])})
                break
        os.system("rm -rf *")
        os.chdir("../")
os.system("rm -rf run/")

print(size_dict)
           
