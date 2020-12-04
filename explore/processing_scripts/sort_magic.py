"""Sorts the magic architecture candidate performance.

Parameters
----------
N : int
    Cluster size.
tech : float
    Technology node (16, 7, 5, 4, 3.0, 3.1).
    3.0 corresponds to F3a in the paper and 3.1 to F3b.
log_dir : str
    Directory holding the run logs.
arc_dir : str
    Directory holding the architecture descriptions.
out_file : str
    Specifies where to write the results.
sort_key : str
    Specifies the sorting key: {delay, area, apd}. 
ignore_circs : Optiona[str], ''
    A space-separated list of circuits to ignore in sorting.
    If the first word is ~, the list will be inverted.
get_median_dict Optional[bool], default = False
    Instead of a single number, print the dictionary of median delays for each circuit.

Returns
-------
None
"""

import os
import argparse
import sys
sys.path.insert(0,'..')

from conf import *

parser = argparse.ArgumentParser()
parser.add_argument("--N")
parser.add_argument("--tech")
parser.add_argument("--log_dir")
parser.add_argument("--arc_dir")
parser.add_argument("--out_file")
parser.add_argument("--sort_key")
parser.add_argument("--ignore_circs")
parser.add_argument("--get_median_dict")

args = parser.parse_args()

get_tech = lambda f : f.split('_')[1][1:]
get_N = lambda f : int(f.split('_')[2][1:])
get_wire = lambda f : f.split('_')[3][1:]
get_circ = lambda f : f.split('_')[-2]
get_seed = lambda f : f.split('_')[-1].rsplit('.', 1)[0]
get_arc = lambda f : '_'.join(f.split('_')[:4])

ignore_circs = []
try:
    ignore_circs = list(args.ignore_circs.split())
except:
    pass

INVERT_IGNORE = False
try:
    if ignore_circs[0] == "~":
        INVERT_IGNORE = True
except:
    pass

GET_MEDIAN_DICT = False
try:
    GET_MEDIAN_DICT = int(args.get_median_dict)
except:
    pass

seed_no = len(seeds)
circ_no = len(ignore_circs) - 1 if INVERT_IGNORE else len(grid_sizes[8]) - len(ignore_circs)

res_dict = {}
for f in os.listdir(args.log_dir):
    try:
        if int(args.N) != get_N(f):
            continue
    except:
        continue
    if args.tech != get_tech(f):
        continue

    arc = get_arc(f)
    circ = get_circ(f)
    if (INVERT_IGNORE and not circ in ignore_circs) or (not INVERT_IGNORE and circ in ignore_circs):
        continue
    try:
        with open("%s/%s" % (args.log_dir, f), "r") as inf:
            td = float(inf.read().strip())
    except:
        continue
    try:
        res_dict[arc][circ].append(td)
    except:
        try:
            res_dict[arc].update({circ : [td]})
        except:
            res_dict.update({arc : {circ : [td]}})

removal_list = set()
processed_res_dict = {}
for arc in res_dict:
    if len(res_dict[arc]) < circ_no:
        continue

    skip = False
    geom_td = 1.0
    for circ in res_dict[arc]:
        if len(res_dict[arc][circ]) < seed_no:
            removal_list.add(arc)
            skip = True
            break
        median = sorted(res_dict[arc][circ])[seed_no / 2]
        geom_td *= median
        if GET_MEDIAN_DICT:
            res_dict[arc][circ] = median

    if skip:
        continue

    geom_td **= (1.0 / circ_no)
    dim = grid_sizes[get_N(arc)][circ]
    try:
        with open("%s/%s_W%d_H%d_padding.log" % (args.arc_dir, arc, dim, dim), "r") as inf:
            lines = inf.readlines()
    except:
        continue
    for line in lines:
        if line.startswith("Active dimensions:"):
            wa = int(line.split()[-4])
            ha = int(line.split()[-2])
        elif line.startswith("Metal dimensions:"):
            wm = int(line.split()[-4])
            hm = int(line.split()[-2])
            break
    a = max(wa, wm) * max(ha, hm) / 1000000.0
    tech = get_tech(arc)
    try:
        processed_res_dict[tech].append((arc, geom_td, a, geom_td * a))
    except:
        processed_res_dict.update({tech : [(arc, geom_td, a, geom_td * a)]})

##########################################################################
def log_sort(res_dict):
    """Logs the sorting results.

    Parameters
    ----------
    res_dict : Dict[str, list]
        A dictionary of performance results per technology.

    Returns
    -------
    None
    """

    txt = "#arc delay[ns] area[um2] apd[nsum2]\n"
    for line in res_dict[tech]:
        for entry in line:
            txt += str(entry) + ' '
        txt += "\n"

    with open(args.out_file, "w") as outf:
        outf.write(txt[:-1])
##########################################################################

if GET_MEDIAN_DICT:
    print(res_dict)

sort_keys = ["delay", "area", "apd"]
processed_res_dict[args.tech].sort(key = lambda arc : [arc[1 + sort_keys.index(args.sort_key)], arc])
log_sort(processed_res_dict)
