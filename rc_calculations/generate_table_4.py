"""Generates Table 4 of the paper (Stacked via resistance).
"""

import os
from inputs import *

template = "\
\\begin{table}[tb]\n\
    \\caption{Resistance of stacked vias connecting the buffer outputs to the \\textsf{My} layers. We assume that the via goes from \\textsf{M2} to \\textsf{M5}.}\n\
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
         H [nm] %s\\\\\n\
         R $[\\Omega]$ %s\\\\\n\
         \\hline\n\
    \\end{tabular}\n\
    \\label{table:stacked_vias}\n\
\\end{table}"

call = "python calc_via_res.py --pitch1 %d --inc_w1 0.1 --pitch2 %d --inc_w2 0.1 --t_barrier_bottom %d --t_barrier_top %d --via_height %f > via_dump.txt"

mx_ars = [2.0, 2.0, 2.0, 2.0, 2.0, 3.0]
#These aspect ratios were previously found by >>find_optimal_ar.py<<

heights = ""
resistances = ""
for node in range(0, len(node_names)):
    pitch1 = mx_pitches[node]
    w = pitch1 / 2.0 * 1.1
    h_via = w
    h_trench = w * mx_ars[node]
    h_stack = 2 * h_trench + 3 * h_via
    pitch2 = my_pitches[node]
    top_barrier = my_barriers[node]
    bottom_barrier = mx_barriers[node]
    os.system(call % (pitch1, pitch2, bottom_barrier, top_barrier, h_stack))
    with open("via_dump.txt", "r") as inf:
        lines = inf.readlines()
    for line in lines:
        if line.startswith("H = "):
            heights += "& %s " % line.split()[2]
        elif line.startswith("R = "):
            resistances += "& %s " % line.split()[2]
    os.system("rm -rf via_dump.txt")

print(template % (heights[:-1], resistances[:-1]))
