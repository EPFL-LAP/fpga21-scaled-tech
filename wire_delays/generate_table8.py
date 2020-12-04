"""Generates Table 8 of the paper (maximum wire lengths per technology.
"""

import os
import sys
sys.path.insert(0,'..')

import tech


template = "\
\\begin{table}\n\
    \\caption{Maximum wire spans for F%s as a function of the cluster size $N$.}\n\
    \\begin{tabular}{c | c c c c c}\n\
        $N$ & 2 & 4 & 8 & 16\\\\\n\
        \\hline\n\
        V %s\\\\\n\
        H %s\\\\\n\
    \\end{tabular}\n\
    \\label{table:max_v_span_F%s}\n\
\\end{table}"

for node in tech.nodes:
    K = 6
    v_lens = ""
    for n in range(1, 5):
        N = 2 ** n
        v_log = "buf_cache/K%dN%dT%s.log" % (K, N, str(node))
        try:
            with open(v_log, "r") as inf:
                lines = inf.readlines()
        except:
            os.system("python global_wires.py --K %d --N %d --tech %s" % (K, N, str(node)))
            with open(v_log, "r") as inf:
                lines = inf.readlines()
        for line in lines:
            if line.startswith("Maximum length = "):
                v_lens += "& %d " % int(line.split()[-1])
                break
    N = 8
    h_lens = ""
    h_log = "buf_cache/HK%dN%dT%s.log" % (K, N, str(node))
    try:
        with open(h_log, "r") as inf:
            lines = inf.readlines()
    except:
        os.system("python global_wires.py --K %d --N %d --tech %s --horizontal 1" % (K, N, str(node)))
        with open(h_log, "r") as inf:
            lines = inf.readlines()
    for line in lines:
        if line.startswith("Maximum length = "):
            h_lens += "& %d " % int(line.split()[-1])
            break

    print(template % (str(node), v_lens[:-1], h_lens[:-1], str(node)))
