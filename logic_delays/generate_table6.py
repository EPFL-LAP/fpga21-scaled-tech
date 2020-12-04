"""Generates Table 6 of the paper (FO4 delays).
"""

import os
import sys
sys.path.insert(0,'..')

import device_geometry

template = "\
\\begin{table}[tb]\n\
    \\caption{FO4 delays at nominal voltages and at 0.7 V.\n\
              The delays at 0.7 V of supply voltage are useful to validate the relative speedup, also shown.\n\
              For this, note that F16 and F7 are two generations apart and that F4 models a possible half-node between F5 and F3.\n\
              The values indicate that a reasonable speedup roughly around 10\\%% between adjacent nodes is maintained.}\n\
    \\begin{tabular}{c c c c c c}\n\
    & F16 & F7 & F5 & F4 & F3\\\\\n\
    \\hline\n\
    At nominal Vdd [ps] %s\\\\\n\
    At 0.7 V [ps] %s\\\\\n\
    $\\Delta$ [\\%%] & %s\\\\\n\
    \\hline\n\
    \\end{tabular}\n\
    \\label{table:fo4}\n\
\\end{table}"

nominal = ""
fixed = ""
deltas = ""
prev = -1
cur = -1

for node in device_geometry.node_names:
    os.system("python sim_fo4.py --tech %d > dump_fo4.txt" % node)
    with open("dump_fo4.txt", "r") as inf:
        lines = inf.readlines()
    for line in lines:
        if line.startswith("FO4 = "):
            nominal += " & %s" % line.split()[2]
    os.system("rm -rf dump_fo4.txt")

    os.system("python sim_fo4.py --tech %d --vdd 0.7 > dump_fo4.txt" % node)
    with open("dump_fo4.txt", "r") as inf:
        lines = inf.readlines()
    for line in lines:
        if line.startswith("FO4 = "):
            td = line.split()[2]
            fixed += " & %s" % td
            cur = float(td)
            if prev >= 0:
                delta = int(round(float(cur - prev) / prev * 100))
                deltas += " & %d" % delta
            prev = cur
    os.system("rm -rf dump_fo4.txt")

print(template % (nominal, fixed, deltas))
