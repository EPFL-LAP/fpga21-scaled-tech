"""Generates Table 3 of the paper (Mx-Mx via resistance).
"""

import os
from inputs import *

template = "\
\\begin{table}[tb]\n\
    \\caption{Resistance of vias. The reported values correspond to the resistance of a single via connecting two neighboring layers in the \\textsf{Mx} group.}\n\
    \\begin{tabular}{"

alignment = ""
titles = ""
for node in range(0, len(node_names )):
    alignment += "c "
    titles += "& %s " % node_names[node]
alignment = alignment[:-1] + "}\n"
titles = "     " + titles[:-1] + "\\\\\n"
template += alignment + titles

template +=\
"         \\hline\n\
         \\textsf{Mx-Mx} $[\\Omega]$ %s\\\\\n\
         \\hline\n\
    \\end{tabular}\n\
    \\label{table:via_res}\n\
\\end{table}"

call = "python calc_via_res.py --pitch1 %d --inc_w1 0.1 --pitch2 %d --inc_w2 0.1 --t_barrier_bottom %d --t_barrier_top %d > via_dump.txt"

resistances = ""

for node in range(0, len(node_names)):
    pitch1 = mx_pitches[node]
    pitch2 = mx_pitches[node]
    top_barrier = mx_barriers[node]
    bottom_barrier = mx_barriers[node]
    os.system(call % (pitch1, pitch2, bottom_barrier, top_barrier))
    with open("via_dump.txt", "r") as inf:
        lines = inf.readlines()
    for line in lines:
        if line.startswith("R = "):
            resistances += "& %s " % line.split()[2]
    os.system("rm -rf via_dump.txt")

print(template % resistances[:-1])
