"""Generates Table 2 of the paper (per um resistance and capacitance).
"""

import os
from inputs import *

template = \
"\\begin{table}[tb]\n\
    \\caption{Wire resistance and capacitance per micrometer length.}\n\
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
"    \\hline\n\
    \\textsf{Mx}\\\\\n\
    \\hline\n\
        $W_{Cu}$ [nm] %s\\\\\n\
        $H_{Cu}$ [nm] %s\\\\\n\
        R' $[\\Omega/\\mu$m] %s\\\\\n\
        C' [fF$/\\mu$m] %s\\\\\n\
    \\hline\n\
    \\textsf{My}\\\\\n\
    \\hline\n\
        $W_{Cu}$ [nm] %s\\\\\n\
        $H_{Cu}$ [nm] %s\\\\\n\
        R' $[\\Omega/\\mu$m] %s\\\\\n\
        C' [fF$/\\mu$m] %s\\\\\n\
        \\hline\n\
    \\end{tabular}\n\
    \\label{table:wire_rc}\n\
\\end{table}"

mx_wcu = ""
mx_hcu = ""
mx_R = ""
mx_C = ""
my_wcu = ""
my_hcu = ""
my_R = ""
my_C = ""

for node in range(0, len(node_names)):
    os.system("python find_optimal_ar.py --ar_max %f --pitch %d --inc_w 0.1 --t_barrier %f --eps_rel %f > ar_dump.txt"\
              % (mx_ar_max[node], mx_pitches[node], mx_barriers[node], mx_eps_rel))
    with open("ar_dump.txt", "r") as inf:
        lines = inf.readlines()
    rd = False
    for line in lines:
        if "Best results" in line:
            rd = True
        if not rd:
            continue
        if line.startswith("Wcu = "):
            mx_wcu += "& %s " % line.split()[2]
        elif line.startswith("Hcu = "):
            mx_hcu += "& %s " % line.split()[2]
        elif line.startswith("R = "):
            mx_R += "& %s " % line.split()[2]
        elif line.startswith("C = "):
            mx_C += "& %s " % line.split()[2]
    os.system("rm -rf ar_dump.txt")

    os.system("python find_optimal_ar.py --ar_max %f --pitch %d --inc_w 0.1 --t_barrier %f --eps_rel %f > ar_dump.txt"\
              % (my_ar_max[node], my_pitches[node], my_barriers[node], my_eps_rel))
    with open("ar_dump.txt", "r") as inf:
        lines = inf.readlines()
    rd = False
    for line in lines:
        if "Best results" in line:
            rd = True
        if not rd:
            continue
        if line.startswith("Wcu = "):
            my_wcu += "& %s " % line.split()[2]
        elif line.startswith("Hcu = "):
            my_hcu += "& %s " % line.split()[2]
        elif line.startswith("R = "):
            my_R += "& %s " % line.split()[2]
        elif line.startswith("C = "):
            my_C += "& %s " % line.split()[2]
    os.system("rm -rf ar_dump.txt")

print(template % (mx_wcu[:-1], mx_hcu[:-1], mx_R[:-1], mx_C[:-1], my_wcu[:-1], my_hcu[:-1], my_R[:-1], my_C[:-1]))
