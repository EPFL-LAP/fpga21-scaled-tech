"""Generates Table 7 of the paper (representative LUT delays).
"""

import os

base_td = 261e-12 #6-LUT delay taken from >>k6_N10_mem32K_40nm<< VTR 8.0 architecture
base_tech = 45 #Closest technology treated by Stillmaker and Baas

template = "\
\\begin{table}\n\
    \\caption{Average input to output delays of a 6-LUT. The values are scaled from the \\emph{K6\\_N10\\_mem32K\\_40nm} VTR architecture file~\\cite{Murray2020}.}\n\
    \\begin{tabular}{c c c c c c}\n\
    & F16 & F7 & F5 & F4 & F3\\\\\n\
    \\hline\n\
    Average Delay [ps] %s\\\\\n\
    \\hline\n\
    \\end{tabular}\n\
    \\label{table:luts}\n\
\\end{table}"

tds = ""
for node in [14, 7, 5, 4, 3]:
    #14 is the closest to 16 that exists in Stillmaker and Baas
    os.system("python scale_logic_delays.py --tf %d --tt %d %g > td_dump.txt"\
              % (base_tech, node, base_td))
    with open("td_dump.txt", "r") as inf:
        lines = inf.readlines()
    td = float(lines[-1].split()[0])
    tds += "& %d " % round(td)
    os.system("rm -rf td_dump.txt")

print template % tds[:-1]
