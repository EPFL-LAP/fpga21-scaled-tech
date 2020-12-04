"""Collects all the results produced by >>cruncher.py<< running VPR and builds a single results dictionary.
Besides keeping the separate geomean results for each magic formula, it computes another median, for each
circuit, over all formulas, and then does a final geomean. This way, the effects of the potentially poor switch-pattern
architecture are cancelled to an extent. Medians are picked per circuit instead of averaging out the per-formula averages,
as different formulas may differently skew the results for each particular circuit. Also, we avoid double processing of
the already averaged-out quantities, which may be hard to do in a sound manner.

Some filename templates may need to be changed, depending on how the rest of the flow was run.
"""

import os
import copy
from ast import literal_eval

sort_call = "python sort_magic.py --arc_dir %s --log_dir %s --out_file %s --N %d --tech %s --sort_key delay --get_median_dict 1 > dict.read"

sort_log_template = "../runner_scripts/all_circs_N8_T%s.sort"
out_file_template = "N%d_T%s_W%d.sort"

get_wire = lambda d : int(d.split('_')[-1])
get_tech = lambda d : d.split('_')[-2][1:]
get_N = lambda d : int(d.split('_')[2][1:])
get_geomean = lambda d : reduce(lambda x, y : x * y, [d[k] for k in d]) ** (1.0 / len(d))

prototype = {"circs" : {}, "wires" : {}}
res_dict = {}
for d in os.listdir("../runner_scripts/"):
    if d.startswith("all_grids_N") and len([c for c in d if c == '_']) == 4 and not "logs" in d:
        arc_dir = "../runner_scripts/" + d
        log_dir = '_'.join(list(arc_dir.split('_')[:-1]) + ["logs"] + [d.split('_')[-1]])
        wire = get_wire(d)
        tech = get_tech(d)
        N = get_N(d)
        if not tech in res_dict:
            res_dict.update({tech : {n : copy.deepcopy(prototype) for n in [2, 4, 8, 16]}})
        with open(sort_log_template % tech, "r") as inf:
            lines = inf.readlines()
        for lcnt, line in enumerate(lines[1:], 1):
            line_wire = int(line.split()[0].split("_W")[1])
            if wire == line_wire:
                wire_index = lcnt
                break
        out_file = out_file_template % (N, tech, wire)
        os.system(sort_call % (arc_dir, log_dir, out_file, N, tech))
        with open(out_file, "r") as inf:
            lines = inf.readlines()
        geom = float(lines[1].split()[1])
        with open("dict.read", "r") as inf:
            txt = inf.read().strip()
        os.system("rm -rf dict.read")
        local_dict = literal_eval(txt)
        local_dict = local_dict[list(local_dict.keys())[0]]
        if abs(geom - get_geomean(local_dict)) > 0.01:
            print "Geomean mismatch!"
            exit(-1)

        res_dict[tech][N]["wires"].update({wire : {"index" : wire_index, "td" : geom}})
        for circ in local_dict:
            try:
                res_dict[tech][N]["circs"][circ].append(local_dict[circ])
            except:
                res_dict[tech][N]["circs"].update({circ : [local_dict[circ]]})

wire_no = 3
for tech in res_dict:
    for N in res_dict[tech]:
        for circ in res_dict[tech][N]["circs"]:
            if len(res_dict[tech][N]["circs"][circ]) != wire_no:
                print "Missing results!"
                exit(-1)
            res_dict[tech][N]["circs"][circ] = sorted(res_dict[tech][N]["circs"][circ])[wire_no / 2]
        res_dict[tech][N].update({"avg" : get_geomean(res_dict[tech][N]["circs"])})
        del res_dict[tech][N]["circs"]

print res_dict

